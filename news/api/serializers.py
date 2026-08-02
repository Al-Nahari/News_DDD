# news/api/serializers.py
from rest_framework import serializers

from accounts.models import Author
from ..models import Article, Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'color', 'icon', 'article_count')


class TagSerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'article_count')


class AuthorSerializer(serializers.ModelSerializer):
    """Deliberately excludes `user` — the public API never exposes which
    account (and therefore which email) sits behind a byline."""

    article_count = serializers.IntegerField(source='articles.count', read_only=True)

    class Meta:
        model = Author
        fields = ('id', 'name', 'avatar', 'bio', 'role', 'article_count')


class ArticleListSerializer(serializers.ModelSerializer):
    """Slim representation for list endpoints — no full content/body."""

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = (
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'is_breaking', 'is_featured',
            'views', 'likes', 'reading_time', 'published_at',
        )
        read_only_fields = fields


class ArticleDetailSerializer(ArticleListSerializer):
    related_articles = serializers.SerializerMethodField()

    class Meta(ArticleListSerializer.Meta):
        fields = ArticleListSerializer.Meta.fields + (
            'content', 'comments', 'meta_title', 'meta_description',
            'created_at', 'updated_at', 'related_articles',
        )
        read_only_fields = fields

    def get_related_articles(self, obj):
        from ..selectors import get_related_articles
        return ArticleListSerializer(get_related_articles(obj), many=True).data


class ArticleWriteSerializer(serializers.ModelSerializer):
    """Used for create/update. `views`, `likes`, `comments`, and `status`
    are deliberately absent: engagement counters are system-managed (see
    news/services.py), and status changes go through the dedicated
    submit-for-review / publish / archive actions so domain rules are
    always enforced."""

    class Meta:
        model = Article
        fields = (
            'title', 'slug', 'excerpt', 'content', 'featured_image',
            'author', 'category', 'tags', 'is_breaking', 'is_featured',
            'reading_time', 'meta_title', 'meta_description', 'scheduled_at',
        )

    def validate_is_featured(self, value):
        instance = getattr(self, 'instance', None)
        if value and (instance is None or instance.status != Article.Status.PUBLISHED):
            raise serializers.ValidationError(
                "Only a published article can be marked as featured."
            )
        return value

    def to_representation(self, instance):
        return ArticleDetailSerializer(instance, context=self.context).data
