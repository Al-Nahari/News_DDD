# news/graphql/schema.py
import graphene
from graphene_django import DjangoObjectType
from graphene_file_upload.scalars import Upload
from django.db.models import Q
from datetime import datetime
from django.utils import timezone

from news.models import Article, Category, Tag, Event
from accounts.models import User, Author


# ======== TYPES ========

class UserType(DjangoObjectType):
    """User Type - GraphQL type for User model"""
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "role", "bio", "avatar", "phone", "is_editor", "is_reporter")


class AuthorType(DjangoObjectType):
    """Author Type - GraphQL type for Author model"""
    class Meta:
        model = Author
        fields = ("id", "name", "avatar", "bio", "role", "user", "created_at", "updated_at")


class CategoryType(DjangoObjectType):
    """Category Type - GraphQL type for Category model"""
    class Meta:
        model = Category
        fields = ("id", "name", "slug", "color", "icon")


class TagType(DjangoObjectType):
    """Tag Type - GraphQL type for Tag model"""
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class ArticleType(DjangoObjectType):
    """Article Type - GraphQL type for Article model"""
    class Meta:
        model = Article
        fields = (
            "id", "title", "slug", "excerpt", "content", "featured_image",
            "author", "category", "tags", "is_breaking", "is_featured",
            "views", "likes", "comments", "reading_time",
            "published_at", "created_at", "updated_at"
        )


class EventType(graphene.ObjectType):
    """Event Type - نوع بيانات الأحداث لـ Event Sourcing"""
    event_type = graphene.String()
    data = graphene.JSONString()
    timestamp = graphene.String()


class MutationResultType(graphene.ObjectType):
    """Mutation Result Type - نوع بيانات النتيجة للتعديلات"""
    success = graphene.Boolean()
    data = graphene.JSONString()
    message = graphene.String()


# ======== INPUT TYPES ========

class AuthorInput(graphene.InputObjectType):
    """Input type for creating/updating author"""
    name = graphene.String(required=True)
    avatar = graphene.String(required=False)
    bio = graphene.String(required=False)
    role = graphene.String(required=False)
    user_id = graphene.Int(required=False)


class CategoryInput(graphene.InputObjectType):
    """Input type for creating/updating category"""
    name = graphene.String(required=True)
    slug = graphene.String(required=True)
    color = graphene.String(required=False)
    icon = graphene.String(required=False)


class TagInput(graphene.InputObjectType):
    """Input type for creating/updating tag"""
    name = graphene.String(required=True)
    slug = graphene.String(required=True)


class ArticleInput(graphene.InputObjectType):
    """Input type for creating/updating article"""
    title = graphene.String(required=True)
    slug = graphene.String(required=True)
    excerpt = graphene.String(required=True)
    content = graphene.String(required=True)
    featured_image = graphene.String(required=False)
    author_id = graphene.Int(required=True)
    category_id = graphene.Int(required=True)
    tag_ids = graphene.List(graphene.Int, required=False)
    is_breaking = graphene.Boolean(required=False, default_value=False)
    is_featured = graphene.Boolean(required=False, default_value=False)
    views = graphene.Int(required=False, default_value=0)
    likes = graphene.Int(required=False, default_value=0)
    comments = graphene.Int(required=False, default_value=0)
    reading_time = graphene.Int(required=False, default_value=1)
    published_at = graphene.String(required=True)


# ======== QUERIES ========

class Query(graphene.ObjectType):
    """
    GraphQL Query - جميع استعلام القراءة للأخبار
    
    المميزات:
    - Resolver Pattern: كل استعلام له محول خاص
    - CQRS: فصل القراءة عن الكتابة
    - DDD: كل استعلام يعبر عن عملية تجارية
    """
    
    # جميع الأخبار
    all_articles = graphene.List(ArticleType)
    
    # خبر محدد
    article_by_id = graphene.Field(ArticleType, article_id=graphene.Int(required=True))
    
    # خبر حسب Slug
    article_by_slug = graphene.Field(ArticleType, slug=graphene.String(required=True))
    
    # أخبار عاجلة
    breaking_articles = graphene.List(ArticleType)
    
    # أخبار مميزة
    featured_articles = graphene.List(ArticleType)
    
    # أخبار منشورة (حالية)
    published_articles = graphene.List(ArticleType)
    
    # بحث في الأخبار
    search_articles = graphene.List(ArticleType, query=graphene.String(required=True))
    
    # أخبار حسب المؤلف
    articles_by_author = graphene.List(ArticleType, author_id=graphene.Int(required=True))
    
    # أخبار حسب التصنيف
    articles_by_category = graphene.List(ArticleType, category_slug=graphene.String(required=True))
    
    # أحداث خبر معين (Event Sourcing)
    article_events = graphene.List(EventType, article_id=graphene.Int(required=True))
    
    # جميع الأحداث المنشورة
    published_events = graphene.List(EventType)
    
    # جميع المستخدمين
    all_users = graphene.List(UserType)
    
    # جميع المؤلفين
    all_authors = graphene.List(AuthorType)
    
    # جميع التصنيفات
    all_categories = graphene.List(CategoryType)
    
    # جميع الوسوم
    all_tags = graphene.List(TagType)
    
    # ======== RESOLVERS ========
    
    def resolve_all_articles(self, info):
        """حل استعلام جميع المقالات"""
        return Article.objects.all().select_related('author', 'category').prefetch_related('tags')
    
    def resolve_article_by_id(self, info, article_id):
        """حل استعلام مقال محدد"""
        try:
            return Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return None
    
    def resolve_article_by_slug(self, info, slug):
        """حل استعلام مقال محدد حسب Slug"""
        try:
            return Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return None
    
    def resolve_breaking_articles(self, info):
        """حل استعلام الأخبار العاجلة"""
        return Article.objects.filter(is_breaking=True).select_related('author', 'category').prefetch_related('tags')
    
    def resolve_featured_articles(self, info):
        """حل استعلام المقالات المميزة"""
        return Article.objects.filter(is_featured=True).select_related('author', 'category').prefetch_related('tags')
    
    def resolve_published_articles(self, info):
        """حل استعلام الأخبار المنشورة (الحالية)"""
        from django.utils import timezone
        return Article.objects.filter(published_at__lte=timezone.now()).select_related('author', 'category').prefetch_related('tags')
    
    def resolve_search_articles(self, info, query):
        """حل استعلام البحث في المقالات"""
        return Article.objects.filter(
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(content__icontains=query)
        ).select_related('author', 'category').prefetch_related('tags')
    
    def resolve_articles_by_author(self, info, author_id):
        """حل استعلام مقالات حسب المؤلف"""
        return Article.objects.filter(author_id=author_id).select_related('author', 'category').prefetch_related('tags')
    
    def resolve_articles_by_category(self, info, category_slug):
        """حل استعلام مقالات حسب التصنيف"""
        try:
            category = Category.objects.get(slug=category_slug)
            return Article.objects.filter(category=category).select_related('author', 'category').prefetch_related('tags')
        except Category.DoesNotExist:
            return []
    
    def resolve_article_events(self, info, article_id):
        """حل استعلام أحداث مقال معين"""
        return Event.objects.filter(data__article_id=article_id).order_by('-timestamp')
    
    def resolve_published_events(self, info):
        """حل استعلام جميع الأحداث المنشورة"""
        return Event.objects.filter(event_type='article_published').order_by('-timestamp')
    
    def resolve_all_users(self, info):
        """حل استعلام جميع المستخدمين"""
        return User.objects.all()
    
    def resolve_all_authors(self, info):
        """حل استعلام جميع المؤلفين"""
        return Author.objects.all()
    
    def resolve_all_categories(self, info):
        """حل استعلام جميع التصنيفات"""
        return Category.objects.all()
    
    def resolve_all_tags(self, info):
        """حل استعلام جميع الوسوم"""
        return Tag.objects.all()


# ======== MUTATIONS ========

class CreateAuthor(graphene.Mutation):
    """Mutation to create a new author"""
    
    class Arguments:
        author_data = AuthorInput(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, author_data):
        try:
            # Get user if provided
            user = None
            if author_data.user_id:
                user = User.objects.get(id=author_data.user_id)
            
            author = Author.objects.create(
                name=author_data.name,
                avatar=author_data.avatar or '',
                bio=author_data.bio or '',
                role=author_data.role or 'reporter',
                user=user
            )
            
            # Create event
            Event.objects.create(
                event_type='author_created',
                data={
                    'author_id': author.id,
                    'name': author.name,
                    'role': author.role,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'author_id': author.id, 'name': author.name},
                message="Author created successfully"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to create author: {str(e)}"
            )


class CreateUser(graphene.Mutation):
    """Mutation to create a new user"""
    
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        role = graphene.String(required=False, default_value='reader')
        bio = graphene.String(required=False)
        phone = graphene.String(required=False)
    
    Output = MutationResultType
    
    def mutate(self, info, username, email, password, role='reader', bio='', phone=''):
        try:
            from accounts.models import User
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                bio=bio,
                phone=phone
            )
            
            # Create event
            Event.objects.create(
                event_type='user_created',
                data={
                    'user_id': user.id,
                    'username': user.username,
                    'role': user.role,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'user_id': user.id, 'username': user.username},
                message="User created successfully"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to create user: {str(e)}"
            )


class CreateCategory(graphene.Mutation):
    """Mutation to create a new category"""
    
    class Arguments:
        category_data = CategoryInput(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, category_data):
        try:
            category = Category.objects.create(
                name=category_data.name,
                slug=category_data.slug,
                color=category_data.color or '#3B82F6',
                icon=category_data.icon or 'category'
            )
            
            # Create event
            Event.objects.create(
                event_type='category_created',
                data={
                    'category_id': category.id,
                    'name': category.name,
                    'slug': category.slug,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'category_id': category.id, 'name': category.name},
                message="Category created successfully"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to create category: {str(e)}"
            )


class CreateTag(graphene.Mutation):
    """Mutation to create a new tag"""
    
    class Arguments:
        tag_data = TagInput(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, tag_data):
        try:
            tag = Tag.objects.create(
                name=tag_data.name,
                slug=tag_data.slug
            )
            
            # Create event
            Event.objects.create(
                event_type='tag_created',
                data={
                    'tag_id': tag.id,
                    'name': tag.name,
                    'slug': tag.slug,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'tag_id': tag.id, 'name': tag.name},
                message="Tag created successfully"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to create tag: {str(e)}"
            )


class CreateArticle(graphene.Mutation):
    """Mutation to create a new article"""
    
    class Arguments:
        article_data = ArticleInput(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, article_data):
        try:
            # Get author and category
            author = Author.objects.get(id=article_data.author_id)
            category = Category.objects.get(id=article_data.category_id)
            
            # Create article
            article = Article.objects.create(
                title=article_data.title,
                slug=article_data.slug,
                excerpt=article_data.excerpt,
                content=article_data.content,
                featured_image=article_data.featured_image,
                author=author,
                category=category,
                is_breaking=article_data.is_breaking,
                is_featured=article_data.is_featured,
                views=article_data.views,
                likes=article_data.likes,
                comments=article_data.comments,
                reading_time=article_data.reading_time,
                published_at=datetime.fromisoformat(article_data.published_at.replace('Z', '+00:00'))
            )
            
            # Add tags if provided
            if article_data.tag_ids:
                tags = Tag.objects.filter(id__in=article_data.tag_ids)
                article.tags.set(tags)
            
            # Create event
            Event.objects.create(
                event_type='article_created',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'slug': article.slug
                },
                message="Article created successfully"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to create article: {str(e)}"
            )


class PublishArticle(graphene.Mutation):
    """Mutation to publish an article"""
    
    class Arguments:
        article_id = graphene.Int(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, article_id):
        try:
            article = Article.objects.get(id=article_id)
            
            # Update published_at if not set
            from django.utils import timezone
            if not article.published_at:
                article.published_at = timezone.now()
                article.save()
            
            # Create event
            Event.objects.create(
                event_type='article_published',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'published_at': article.published_at.isoformat(),
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'article_id': article.id, 'title': article.title},
                message="Article published successfully"
            )
        except Article.DoesNotExist:
            return MutationResultType(
                success=False,
                data=None,
                message="Article not found"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to publish article: {str(e)}"
            )


class UpdateArticle(graphene.Mutation):
    """Mutation to update an article"""
    
    class Arguments:
        article_id = graphene.Int(required=True)
        title = graphene.String(required=False)
        content = graphene.String(required=False)
        excerpt = graphene.String(required=False)
        is_breaking = graphene.Boolean(required=False)
        is_featured = graphene.Boolean(required=False)
    
    Output = MutationResultType
    
    def mutate(self, info, article_id, **kwargs):
        try:
            article = Article.objects.get(id=article_id)
            
            # Update fields
            for field, value in kwargs.items():
                if value is not None:
                    setattr(article, field, value)
            
            article.save()
            
            # Create event
            Event.objects.create(
                event_type='article_updated',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'updated_fields': list(kwargs.keys()),
                    'timestamp': timezone.now().isoformat()
                }
            )
            
            return MutationResultType(
                success=True,
                data={'article_id': article.id, 'title': article.title},
                message="Article updated successfully"
            )
        except Article.DoesNotExist:
            return MutationResultType(
                success=False,
                data=None,
                message="Article not found"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to update article: {str(e)}"
            )


class DeleteArticle(graphene.Mutation):
    """Mutation to delete an article"""
    
    class Arguments:
        article_id = graphene.Int(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, article_id):
        try:
            article = Article.objects.get(id=article_id)
            
            # Create event before deletion
            Event.objects.create(
                event_type='article_deleted',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'deleted_at': timezone.now().isoformat()
                }
            )
            
            article.delete()
            
            return MutationResultType(
                success=True,
                data={'article_id': article_id},
                message="Article deleted successfully"
            )
        except Article.DoesNotExist:
            return MutationResultType(
                success=False,
                data=None,
                message="Article not found"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to delete article: {str(e)}"
            )


class IncrementViews(graphene.Mutation):
    """Mutation to increment article views"""
    
    class Arguments:
        article_id = graphene.Int(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, article_id):
        try:
            article = Article.objects.get(id=article_id)
            article.views += 1
            article.save()
            
            return MutationResultType(
                success=True,
                data={'article_id': article.id, 'views': article.views},
                message="Views incremented successfully"
            )
        except Article.DoesNotExist:
            return MutationResultType(
                success=False,
                data=None,
                message="Article not found"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to increment views: {str(e)}"
            )


class IncrementLikes(graphene.Mutation):
    """Mutation to increment article likes"""
    
    class Arguments:
        article_id = graphene.Int(required=True)
    
    Output = MutationResultType
    
    def mutate(self, info, article_id):
        try:
            article = Article.objects.get(id=article_id)
            article.likes += 1
            article.save()
            
            return MutationResultType(
                success=True,
                data={'article_id': article.id, 'likes': article.likes},
                message="Likes incremented successfully"
            )
        except Article.DoesNotExist:
            return MutationResultType(
                success=False,
                data=None,
                message="Article not found"
            )
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to increment likes: {str(e)}"
            )


class BulkInsertData(graphene.Mutation):
    """Mutation to bulk insert all mock data"""
    
    class Arguments:
        pass
    
    Output = MutationResultType
    
    def mutate(self, info):
        try:
            # Insert Users
            users_data = [
                {
                    "username": "ahmed_mohammed",
                    "email": "ahmed@news.com",
                    "password": "password123",
                    "role": "reporter",
                    "bio": "مراسل سياسي متخصص في الشؤون الدولية",
                    "phone": "+966500000001"
                },
                {
                    "username": "fatima_alatebi",
                    "email": "fatima@news.com",
                    "password": "password123",
                    "role": "editor",
                    "bio": "خبيرة اقتصادية وتحليلية",
                    "phone": "+966500000002"
                },
                {
                    "username": "khaled_alsalem",
                    "email": "khaled@news.com",
                    "password": "password123",
                    "role": "reporter",
                    "bio": "مراسل رياضي",
                    "phone": "+966500000003"
                },
                {
                    "username": "nora_alharbi",
                    "email": "nora@news.com",
                    "password": "password123",
                    "role": "editor",
                    "bio": "كاتبة ومحررة",
                    "phone": "+966500000004"
                }
            ]
            
            from accounts.models import User
            users = []
            for data in users_data:
                try:
                    user = User.objects.get(username=data['username'])
                    user.email = data['email']
                    user.role = data['role']
                    user.bio = data['bio']
                    user.phone = data['phone']
                    user.save()
                except User.DoesNotExist:
                    user = User.objects.create_user(**data)
                users.append(user)
            
            # Insert Authors
            authors_data = [
                {
                    "name": "أحمد محمد العتيبي",
                    "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
                    "bio": "مراسل سياسي متخصص في الشؤون الدولية والقمم العالمية",
                    "role": "reporter"
                },
                {
                    "name": "فاطمة عبدالله الحربي",
                    "avatar": "https://randomuser.me/api/portraits/women/44.jpg",
                    "bio": "خبيرة اقتصادية وتحليلية markets و stocks",
                    "role": "editor"
                },
                {
                    "name": "خالد سالم السالم",
                    "avatar": "https://randomuser.me/api/portraits/men/28.jpg",
                    "bio": "مراسل رياضي متخصص في كرة القدم والدوري السعودي",
                    "role": "reporter"
                },
                {
                    "name": "نورا أحمد الشمري",
                    "avatar": "https://randomuser.me/api/portraits/women/68.jpg",
                    "bio": "كاتبة ومحررة متخصصة في الصحة والطب",
                    "role": "editor"
                }
            ]
            
            authors = []
            for data in authors_data:
                author = Author.objects.create(**data)
                authors.append(author)
            
            # Insert Categories
            categories_data = [
                {"name": "السياسة", "slug": "politics", "color": "#3B82F6", "icon": "landmark"},
                {"name": "الاقتصاد", "slug": "economy", "color": "#10B981", "icon": "chart-line"},
                {"name": "الرياضة", "slug": "sports", "color": "#F59E0B", "icon": "trophy"},
                {"name": "التقنية", "slug": "technology", "color": "#8B5CF6", "icon": "microchip"},
                {"name": "الصحة", "slug": "health", "color": "#EF4444", "icon": "heartbeat"}
            ]
            
            categories = []
            for data in categories_data:
                try:
                    category = Category.objects.get(slug=data['slug'])
                    category.name = data['name']
                    category.color = data['color']
                    category.icon = data['icon']
                    category.save()
                except Category.DoesNotExist:
                    category = Category.objects.create(**data)
                categories.append(category)
            
            # Insert Tags
            tags_data = [
                {"name": "القمة", "slug": "summit"},
                {"name": "السلام", "slug": "peace"},
                {"name": "بترول", "slug": "oil"},
                {"name": "أوبك", "slug": "opec"},
                {"name": "ذكاء اصطناعي", "slug": "ai"},
                {"name": "تقنية", "slug": "tech"},
                {"name": "صحة", "slug": "health"},
                {"name": "رياضة", "slug": "sports"},
                {"name": "لقاح", "slug": "vaccine"},
                {"name": "أسهم", "slug": "stocks"},
                {"name": "اقتصاد", "slug": "economy"}
            ]
            
            tags = []
            for data in tags_data:
                try:
                    tag = Tag.objects.get(slug=data['slug'])
                    tag.name = data['name']
                    tag.save()
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(**data)
                tags.append(tag)
            
            # Insert Articles
            articles_data = [
                {
                    "title": "قمة دولية في الرياض لبحث السلام في المنطقة بمشاركة قادة من 15 دولة",
                    "slug": "international-peace-summit-riyadh",
                    "excerpt": "انطلقت اليوم القمة الدولية للسلام في العاصمة السعودية الرياض بحضور قادة دول وممثلي منظمات دولية لبحث سبل إنهاء الصراعات في المنطقة.",
                    "content": "انطلقت اليوم القمة الدولية للسلام في العاصمة السعودية الرياض بحضور قادة دول وممثلي منظمات دولية لبحث سبل إنهاء الصراعات في المنطقة. وتركز القمة على تعزيز التعاون الاقتصادي والأمني بين الدول المشاركة.",
                    "featured_image": "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=800&h=500&fit=crop",
                    "author_id": 1,
                    "category_id": 1,
                    "tag_ids": [1, 2],
                    "is_breaking": True,
                    "is_featured": True,
                    "views": 15420,
                    "likes": 1250,
                    "comments": 340,
                    "reading_time": 4,
                    "published_at": timezone.now().isoformat()
                },
                {
                    "title": "ارتفاع كبير في أسعار النفط بعد قرارات أوبك الأخيرة",
                    "slug": "oil-prices-rise-opec-decision",
                    "excerpt": "شهدت أسعار النفط ارتفاعاً ملحوظاً بعد أن أعلنت منظمة البلدان المصدرة للبترول عن خفض الإنتاج.",
                    "content": "شهدت أسعار النفط العالمية ارتفاعاً ملحوظاً بعد أن أعلنت منظمة البلدان المصدرة للبترول وحلفائها عن خفض الإنتاج بنسبة 5%. ويعزى هذا الارتفاع إلى زيادة الطلب العالمي.",
                    "featured_image": "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=800&h=500&fit=crop",
                    "author_id": 2,
                    "category_id": 2,
                    "tag_ids": [3, 4],
                    "is_breaking": False,
                    "is_featured": True,
                    "views": 8920,
                    "likes": 640,
                    "comments": 120,
                    "reading_time": 3,
                    "published_at": timezone.now().isoformat()
                },
                {
                    "title": "انطلاق فعاليات القمة العالمية للذكاء الاصطناعي في دبي",
                    "slug": "ai-summit-dubai-launch",
                    "excerpt": "انطلقت فعاليات القمة العالمية للذكاء الاصطناعي في دبي بمشاركة خبراء وشركات تقنية عالمية.",
                    "content": "انطلقت اليوم فعاليات القمة العالمية للذكاء الاصطناعي في دبي بمشاركة أكثر من 500 خبير وشركة تقنية عالمية. وتركز القمة على مستقبل الذكاء الاصطناعي وتطبيقاته.",
                    "featured_image": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=800&h=500&fit=crop",
                    "author_id": 3,
                    "category_id": 4,
                    "tag_ids": [5, 6],
                    "is_breaking": False,
                    "is_featured": False,
                    "views": 6540,
                    "likes": 420,
                    "comments": 89,
                    "reading_time": 5,
                    "published_at": timezone.now().isoformat()
                },
                {
                    "title": "دراسة جديدة تكشف عن فوائد مذهلة للتمارين الرياضية",
                    "slug": "study-reveals-benefits-exercise",
                    "excerpt": "أظهرت دراسة جديدة أن ممارسة الرياضة بانتظام يمكن أن تزيد من العمر المتوقع.",
                    "content": "أظهرت دراسة جديدة أجريت على آلاف المشاركين أن ممارسة الرياضة بانتظام يمكن أن تزيد من العمر المتوقع بنسبة 20%. وتوصل الباحثون إلى هذه النتائج بعد متابعة المشاركين.",
                    "featured_image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&h=500&fit=crop",
                    "author_id": 4,
                    "category_id": 3,
                    "tag_ids": [7, 8],
                    "is_breaking": False,
                    "is_featured": False,
                    "views": 4230,
                    "likes": 380,
                    "comments": 65,
                    "reading_time": 4,
                    "published_at": timezone.now().isoformat()
                },
                {
                    "title": "الكشف عن تطوير لقاح جديد لمرض خطير",
                    "slug": "new-vaccine-development",
                    "excerpt": "أعلنت شرطة دوائية رائدة عن تطوير لقاح جديد لمرض خطير يهدد ملايين الأشخاص.",
                    "content": "أعلنت شركة دوائية رائدة عن تطوير لقاح جديد لمرض خطير يهدد ملايين الأشخاص حول العالم. وأظهرت التجارب الأولية نجاحاً كبيراً.",
                    "featured_image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&h=500&fit=crop",
                    "author_id": 2,
                    "category_id": 5,
                    "tag_ids": [9, 7],
                    "is_breaking": True,
                    "is_featured": False,
                    "views": 12300,
                    "likes": 890,
                    "comments": 210,
                    "reading_time": 3,
                    "published_at": timezone.now().isoformat()
                },
                {
                    "title": "انهيار في سوق الأسهم العالمية بسبب التوترات الاقتصادية",
                    "slug": "stock-market-crash",
                    "excerpt": "شهدت الأسواق المالية العالمية انهياراً كبيراً بسبب التوترات الاقتصادية الجيوسياسية.",
                    "content": "شهدت الأسواق المالية العالمية انهياراً كبيراً بسبب التوترات الاقتصادية الجيوسياسية. وانخفض مؤشرات الأسهم الرئيسية.",
                    "featured_image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=500&fit=crop",
                    "author_id": 2,
                    "category_id": 2,
                    "tag_ids": [10, 11],
                    "is_breaking": True,
                    "is_featured": False,
                    "views": 18900,
                    "likes": 1200,
                    "comments": 450,
                    "reading_time": 6,
                    "published_at": timezone.now().isoformat()
                }
            ]
            
            articles_created = 0
            for article_data in articles_data:
                try:
                    author = Author.objects.get(id=article_data['author_id'])
                    category = Category.objects.get(id=article_data['category_id'])
                    
                    article, created = Article.objects.get_or_create(
                        slug=article_data['slug'],
                        defaults={
                            'title': article_data['title'],
                            'excerpt': article_data['excerpt'],
                            'content': article_data['content'],
                            'featured_image': article_data['featured_image'],
                            'author': author,
                            'category': category,
                            'is_breaking': article_data['is_breaking'],
                            'is_featured': article_data['is_featured'],
                            'views': article_data['views'],
                            'likes': article_data['likes'],
                            'comments': article_data['comments'],
                            'reading_time': article_data['reading_time'],
                            'published_at': datetime.fromisoformat(article_data['published_at'].replace('Z', '+00:00'))
                        }
                    )
                    
                    if created:
                        # Add tags
                        tags_to_add = Tag.objects.filter(id__in=article_data['tag_ids'])
                        article.tags.set(tags_to_add)
                        articles_created += 1
                        
                        # Create event
                        Event.objects.create(
                            event_type='article_created',
                            data={
                                'article_id': article.id,
                                'title': article.title,
                                'slug': article.slug,
                                'timestamp': timezone.now().isoformat()
                            }
                        )
                        
                except Exception as e:
                    print(f"Error creating article {article_data['slug']}: {e}")
                    continue
            
            return MutationResultType(
                success=True,
                data={
                    'users': len(users),
                    'authors': len(authors),
                    'categories': len(categories),
                    'tags': len(tags),
                    'articles': articles_created
                },
                message=f"Data inserted successfully! Created: {len(users)} users, {len(authors)} authors, {len(categories)} categories, {len(tags)} tags, {articles_created} articles"
            )
            
        except Exception as e:
            return MutationResultType(
                success=False,
                data=None,
                message=f"Failed to insert data: {str(e)}"
            )


class Mutation(graphene.ObjectType):
    """
    GraphQL Mutations - جميع التعديلات للニュース
    
    المميزات:
    - كل mutation له handler خاص
    - CQRS: فصل القراءة عن الكتابة
    - DDD: كل mutation تمثل عملية تجارية
    """
    create_author = CreateAuthor.Field()
    create_user = CreateUser.Field()
    create_category = CreateCategory.Field()
    create_tag = CreateTag.Field()
    create_article = CreateArticle.Field()
    publish_article = PublishArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()
    increment_views = IncrementViews.Field()
    increment_likes = IncrementLikes.Field()
    bulk_insert_data = BulkInsertData.Field()


# ======== SCHEMA ========

schema = graphene.Schema(query=Query, mutation=Mutation)