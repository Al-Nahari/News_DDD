# news/api/views.py
from django.db import connection
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import Author
from .. import selectors, services
from ..models import Article, Category, Tag
from .filters import ArticleFilter
from .permissions import ArticlePermission, CanManageTaxonomy, CanReviewAndPublish
from .serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    ArticleWriteSerializer,
    AuthorSerializer,
    CategorySerializer,
    TagSerializer,
)


def ok(data, http_status=status.HTTP_200_OK):
    return Response({'success': True, 'data': data}, status=http_status)


class ArticleViewSet(viewsets.ModelViewSet):
    """Public reads are limited to published articles; every write is
    permission-checked in ArticlePermission, and lifecycle transitions
    (publish/archive/submit) are separate actions so the domain rules in
    news/services.py are always applied — a client can never PATCH a
    draft straight into "published"."""

    permission_classes = [ArticlePermission]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArticleFilter
    search_fields = ['title', 'excerpt', 'content']
    ordering_fields = ['published_at', 'created_at', 'views', 'likes']

    def get_queryset(self):
        user = self.request.user
        if self.request.method in ('GET', 'HEAD', 'OPTIONS') and not (
            user.is_authenticated and user.role in ('admin', 'editor', 'reporter')
        ):
            return selectors.get_published_articles()
        # Staff roles can see their own drafts/pending/archived articles too.
        from django.db.models import Q
        qs = Article.objects.select_related('author', 'category').prefetch_related('tags')
        if user.is_authenticated and user.role == 'reporter' and not user.is_superuser:
            qs = qs.filter(Q(status=Article.Status.PUBLISHED) | Q(author__user=user))
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ArticleWriteSerializer
        return ArticleDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        services.increment_article_view(instance)
        instance.refresh_from_db(fields=['views'])
        serializer = self.get_serializer(instance)
        return ok(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page if page is not None else queryset, many=True)
        if page is not None:
            paginated = self.get_paginated_response(serializer.data)
            return ok(paginated.data)
        return ok(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ok(serializer.data, status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ok(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return ok({'deleted': True})

    @action(detail=True, methods=['post'], permission_classes=[ArticlePermission])
    def submit_for_review(self, request, slug=None):
        article = self.get_object()
        services.submit_for_review(article, request.user)
        return ok(ArticleDetailSerializer(article).data)

    @action(detail=True, methods=['post'], permission_classes=[CanReviewAndPublish])
    def publish(self, request, slug=None):
        article = self.get_object()
        services.publish_article(article, request.user)
        return ok(ArticleDetailSerializer(article).data)

    @action(detail=True, methods=['post'], permission_classes=[CanReviewAndPublish])
    def archive(self, request, slug=None):
        article = self.get_object()
        services.archive_article(article, request.user)
        return ok(ArticleDetailSerializer(article).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, slug=None):
        article = self.get_object()
        created, like_count = services.like_article(article, request.user)
        return ok({'liked': True, 'already_liked': not created, 'likes': like_count})


@api_view(['GET'])
@permission_classes([AllowAny])
def breaking_news(request):
    articles = selectors.get_breaking_articles()
    return ok(ArticleListSerializer(articles, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def featured_news(request):
    articles = selectors.get_featured_articles()
    return ok(ArticleListSerializer(articles, many=True).data)


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageTaxonomy]
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return selectors.get_categories_with_article_counts()


class TagViewSet(viewsets.ModelViewSet):
    permission_classes = [CanManageTaxonomy]
    serializer_class = TagSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return selectors.get_tags_with_article_counts()


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = AuthorSerializer
    queryset = Author.objects.all()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False
    body = {
        'status': 'healthy' if db_ok else 'degraded',
        'timestamp': timezone.now().isoformat(),
        'service': 'news-api',
        'checks': {'database': db_ok},
    }
    return Response(body, status=status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE)
