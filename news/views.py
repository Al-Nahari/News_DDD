# news/views.py
"""Legacy, unversioned REST endpoints.

These paths (/api/news/, /api/breaking/, /api/featured/, /api/categories/,
/api/tags/, /api/authors/) are kept as thin, read-only, GET-compatible
wrappers around the new selectors/serializers so an existing frontend that
still calls them doesn't break during the migration to /api/v1/.

Everything that used to allow unauthenticated writes has been removed:
    * CreateArticleAPIView, and PUT/DELETE on ArticleDetailAPIView
    * IncrementViewsAPIView / IncrementLikesAPIView (client-controlled counters)
    * BulkInsertDataAPIView (mock-data endpoint with hardcoded credentials)
    * UsersAPIView (publicly exposed user email addresses)
Those capabilities now live in /api/v1/ behind authentication and
role-based permissions — see news/api/views.py.
"""
from django.http import JsonResponse
from django.views import View

from . import selectors
from .api.serializers import (
    ArticleDetailSerializer,
    ArticleListSerializer,
    AuthorSerializer,
    CategorySerializer,
    TagSerializer,
)
from .models import Article
from .services import increment_article_view


class ArticleListAPIView(View):
    """GET /api/news/ — filterable list of published articles."""

    def get(self, request):
        articles = selectors.get_published_articles()
        category = request.GET.get('category')
        tag = request.GET.get('tag')
        author = request.GET.get('author')
        search = request.GET.get('q')
        slug = request.GET.get('slug')

        if slug:
            articles = articles.filter(slug=slug)
        if category:
            articles = articles.filter(category__slug=category)
        if tag:
            articles = articles.filter(tags__slug=tag)
        if author:
            articles = articles.filter(author_id=author)
        if search:
            articles = selectors.search_articles(search)
        if request.GET.get('is_breaking'):
            articles = articles.filter(is_breaking=True)
        if request.GET.get('is_featured'):
            articles = articles.filter(is_featured=True)

        data = ArticleListSerializer(articles.distinct()[:100], many=True).data
        return JsonResponse({'articles': data, 'count': len(data)}, status=200)


class ArticleDetailAPIView(View):
    """GET /api/news/<id>/ — read-only. Writes moved to /api/v1/articles/<slug>/."""

    def get(self, request, article_id):
        try:
            article = selectors.get_published_articles().get(id=article_id)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)

        increment_article_view(article)
        article.refresh_from_db(fields=['views'])
        data = ArticleDetailSerializer(article).data
        return JsonResponse({'article': data}, status=200)


class BreakingNewsAPIView(View):
    def get(self, request):
        data = ArticleListSerializer(selectors.get_breaking_articles(), many=True).data
        return JsonResponse({'breaking_news': data, 'count': len(data)}, status=200)


class FeaturedArticlesAPIView(View):
    def get(self, request):
        data = ArticleListSerializer(selectors.get_featured_articles(), many=True).data
        return JsonResponse({'featured_articles': data, 'count': len(data)}, status=200)


class CategoriesAPIView(View):
    def get(self, request):
        data = CategorySerializer(selectors.get_categories_with_article_counts(), many=True).data
        return JsonResponse({'categories': data, 'count': len(data)}, status=200)


class TagsAPIView(View):
    def get(self, request):
        data = TagSerializer(selectors.get_tags_with_article_counts(), many=True).data
        return JsonResponse({'tags': data, 'count': len(data)}, status=200)


class AuthorsAPIView(View):
    def get(self, request):
        from accounts.models import Author
        data = AuthorSerializer(Author.objects.all(), many=True).data
        return JsonResponse({'authors': data, 'count': len(data)}, status=200)


def health_check(request):
    from .api.views import health_check as _health_check
    return _health_check(request)
