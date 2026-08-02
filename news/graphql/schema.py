# news/graphql/schema.py
"""GraphQL schema, kept for backward compatibility while frontend usage is
confirmed (see refactor report). All mutations now enforce the same
role-based rules as the REST API instead of being open to anyone; the
mock-data BulkInsertData mutation and the unauthenticated counter mutations
have been removed entirely, and reads no longer leak unpublished drafts or
user emails to anonymous callers.
"""
import graphene
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from django.db.models import Q
from django.utils import timezone

from accounts import permissions as roles
from accounts.models import Author, User
from news import selectors, services
from news.models import Article, AuditLog, Category, Tag


def _require(condition, message="Permission denied."):
    if not condition:
        raise GraphQLError(message)


def _user(info):
    return getattr(info.context, 'user', None)


# ======== TYPES ========

class UserType(DjangoObjectType):
    """No `email`/`phone` — those are account details, not public byline
    info. Use AuthorType for what the frontend renders publicly."""

    class Meta:
        model = User
        fields = ("id", "username", "role")


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = ("id", "name", "avatar", "bio", "role", "created_at", "updated_at")


class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "color", "icon")


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ArticleType(DjangoObjectType):
    class Meta:
        model = Article
        fields = (
            "id", "title", "slug", "excerpt", "content", "featured_image",
            "author", "category", "tags", "status", "is_breaking", "is_featured",
            "views", "likes", "comments", "reading_time",
            "published_at", "created_at", "updated_at",
        )


class MutationResultType(graphene.ObjectType):
    success = graphene.Boolean()
    data = graphene.JSONString()
    message = graphene.String()


# ======== INPUT TYPES ========

class AuthorInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    avatar = graphene.String(required=False)
    bio = graphene.String(required=False)
    role = graphene.String(required=False)
    user_id = graphene.Int(required=False)


class CategoryInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    color = graphene.String(required=False)
    icon = graphene.String(required=False)


class TagInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    slug = graphene.String(required=True)


class ArticleInput(graphene.InputObjectType):
    """No `views`/`likes`/`comments` — those are system-managed (see
    news/services.py) and can't be set by a client."""

    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    excerpt = graphene.String(required=True)
    content = graphene.String(required=True)
    featured_image = graphene.String(required=False)
    author_id = graphene.Int(required=True)
    category_id = graphene.Int(required=True)
    tag_ids = graphene.List(graphene.Int, required=False)
    is_breaking = graphene.Boolean(required=False, default_value=False)
    reading_time = graphene.Int(required=False, default_value=1)


# ======== QUERIES ========

class Query(graphene.ObjectType):
    all_articles = graphene.List(ArticleType)
    article_by_id = graphene.Field(ArticleType, article_id=graphene.Int(required=True))
    article_by_slug = graphene.Field(ArticleType, slug=graphene.String(required=True))
    breaking_articles = graphene.List(ArticleType)
    featured_articles = graphene.List(ArticleType)
    published_articles = graphene.List(ArticleType)
    search_articles = graphene.List(ArticleType, query=graphene.String(required=True))
    articles_by_author = graphene.List(ArticleType, author_id=graphene.Int(required=True))
    articles_by_category = graphene.List(ArticleType, category_slug=graphene.String(required=True))
    all_authors = graphene.List(AuthorType)
    all_categories = graphene.List(CategoryType)
    all_tags = graphene.List(TagType)
    # Staff-only: full user list and unfiltered article list (drafts included).
    all_users = graphene.List(UserType)
    all_articles_admin = graphene.List(ArticleType)

    def _visible_articles(self, info):
        """Anonymous/reader callers only ever see published articles;
        drafts and pending-review articles are never exposed publicly."""
        user = _user(info)
        if user is not None and roles.is_reporter(user):
            return Article.objects.select_related('author', 'category').prefetch_related('tags')
        return selectors.get_published_articles()

    def resolve_all_articles(self, info):
        return self._visible_articles(info)

    def resolve_article_by_id(self, info, article_id):
        return self._visible_articles(info).filter(id=article_id).first()

    def resolve_article_by_slug(self, info, slug):
        return self._visible_articles(info).filter(slug=slug).first()

    def resolve_breaking_articles(self, info):
        return selectors.get_breaking_articles()

    def resolve_featured_articles(self, info):
        return selectors.get_featured_articles()

    def resolve_published_articles(self, info):
        return selectors.get_published_articles()

    def resolve_search_articles(self, info, query):
        return selectors.search_articles(query)

    def resolve_articles_by_author(self, info, author_id):
        return self._visible_articles(info).filter(author_id=author_id)

    def resolve_articles_by_category(self, info, category_slug):
        return self._visible_articles(info).filter(category__slug=category_slug)

    def resolve_all_authors(self, info):
        return Author.objects.all()

    def resolve_all_categories(self, info):
        return selectors.get_categories_with_article_counts()

    def resolve_all_tags(self, info):
        return selectors.get_tags_with_article_counts()

    def resolve_all_users(self, info):
        _require(roles.can_manage_users(_user(info)))
        return User.objects.all()

    def resolve_all_articles_admin(self, info):
        _require(roles.is_reporter(_user(info)))
        return Article.objects.select_related('author', 'category').prefetch_related('tags')


# ======== MUTATIONS ========

class CreateAuthor(graphene.Mutation):
    class Arguments:
        author_data = AuthorInput(required=True)

    Output = MutationResultType

    def mutate(self, info, author_data):
        _require(roles.can_manage_users(_user(info)))
        user = User.objects.get(id=author_data.user_id) if author_data.user_id else None
        author = Author.objects.create(
            name=author_data.name,
            avatar=author_data.avatar or '',
            bio=author_data.bio or '',
            role=author_data.role or 'reporter',
            user=user,
        )
        return MutationResultType(success=True, data={'author_id': author.id, 'name': author.name}, message="Author created successfully")


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        role = graphene.String(required=False, default_value='reader')
        bio = graphene.String(required=False)
        phone = graphene.String(required=False)

    Output = MutationResultType

    def mutate(self, info, username, email, password, role='reader', bio='', phone=''):
        # User/account creation is an admin action, not public self-signup —
        # this schema has no separate "register" mutation on purpose.
        _require(roles.can_manage_users(_user(info)))
        user = User.objects.create_user(username=username, email=email, password=password, role=role, bio=bio, phone=phone)
        return MutationResultType(success=True, data={'user_id': user.id, 'username': user.username}, message="User created successfully")


class CreateCategory(graphene.Mutation):
    class Arguments:
        category_data = CategoryInput(required=True)

    Output = MutationResultType

    def mutate(self, info, category_data):
        _require(roles.can_manage_taxonomy(_user(info)))
        category = Category.objects.create(
            name=category_data.name, slug=category_data.slug,
            color=category_data.color or '#3B82F6', icon=category_data.icon or 'category',
        )
        return MutationResultType(success=True, data={'category_id': category.id, 'name': category.name}, message="Category created successfully")


class CreateTag(graphene.Mutation):
    class Arguments:
        tag_data = TagInput(required=True)

    Output = MutationResultType

    def mutate(self, info, tag_data):
        _require(roles.can_manage_taxonomy(_user(info)))
        tag = Tag.objects.create(name=tag_data.name, slug=tag_data.slug)
        return MutationResultType(success=True, data={'tag_id': tag.id, 'name': tag.name}, message="Tag created successfully")


class CreateArticle(graphene.Mutation):
    class Arguments:
        article_data = ArticleInput(required=True)

    Output = MutationResultType

    def mutate(self, info, article_data):
        _require(roles.can_write_articles(_user(info)))
        author = Author.objects.get(id=article_data.author_id)
        category = Category.objects.get(id=article_data.category_id)
        article = Article.objects.create(
            title=article_data.title,
            slug=article_data.slug,
            excerpt=article_data.excerpt,
            content=article_data.content,
            featured_image=article_data.featured_image,
            author=author,
            category=category,
            is_breaking=article_data.is_breaking,
            reading_time=article_data.reading_time,
            status=Article.Status.DRAFT,
        )
        if article_data.tag_ids:
            article.tags.set(Tag.objects.filter(id__in=article_data.tag_ids))
        return MutationResultType(
            success=True,
            data={'article_id': article.id, 'title': article.title, 'slug': article.slug},
            message="Article created successfully (as draft)",
        )


class PublishArticle(graphene.Mutation):
    class Arguments:
        article_id = graphene.Int(required=True)

    Output = MutationResultType

    def mutate(self, info, article_id):
        user = _user(info)
        _require(roles.can_review_and_publish(user))
        article = Article.objects.get(id=article_id)
        services.publish_article(article, user)
        return MutationResultType(success=True, data={'article_id': article.id, 'title': article.title}, message="Article published successfully")


class UpdateArticle(graphene.Mutation):
    class Arguments:
        article_id = graphene.Int(required=True)
        title = graphene.String(required=False)
        content = graphene.String(required=False)
        excerpt = graphene.String(required=False)
        is_breaking = graphene.Boolean(required=False)

    Output = MutationResultType

    def mutate(self, info, article_id, **kwargs):
        user = _user(info)
        article = Article.objects.get(id=article_id)
        _require(roles.can_edit_article(user, article))
        for field, value in kwargs.items():
            if value is not None:
                setattr(article, field, value)
        article.save()
        return MutationResultType(success=True, data={'article_id': article.id, 'title': article.title}, message="Article updated successfully")


class DeleteArticle(graphene.Mutation):
    class Arguments:
        article_id = graphene.Int(required=True)

    Output = MutationResultType

    def mutate(self, info, article_id):
        user = _user(info)
        article = Article.objects.get(id=article_id)
        _require(roles.can_delete_article(user, article))
        article.delete()
        return MutationResultType(success=True, data={'article_id': article_id}, message="Article deleted successfully")


class LikeArticle(graphene.Mutation):
    """Replaces the old, unauthenticated IncrementLikes mutation — liking
    now requires a signed-in user and can't be repeated by the same user."""

    class Arguments:
        article_id = graphene.Int(required=True)

    Output = MutationResultType

    def mutate(self, info, article_id):
        user = _user(info)
        _require(user is not None and user.is_authenticated, "You must be signed in to like an article.")
        article = Article.objects.get(id=article_id)
        _created, like_count = services.like_article(article, user)
        return MutationResultType(success=True, data={'article_id': article.id, 'likes': like_count}, message="Liked")


class Mutation(graphene.ObjectType):
    create_author = CreateAuthor.Field()
    create_user = CreateUser.Field()
    create_category = CreateCategory.Field()
    create_tag = CreateTag.Field()
    create_article = CreateArticle.Field()
    publish_article = PublishArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()
    like_article = LikeArticle.Field()


# ======== SCHEMA ========

schema = graphene.Schema(query=Query, mutation=Mutation)
