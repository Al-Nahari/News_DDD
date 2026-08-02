# news/selectors.py
"""Read-side query helpers.

These exist so that "what counts as a publicly visible article" and the
select_related/prefetch_related needed to avoid N+1 queries are defined once
and reused by the REST API, GraphQL, and the admin — instead of every view
repeating `Article.objects.filter(status=..., published_at__lte=...)`.
"""
from django.db.models import Count
from django.utils import timezone

from .models import Article


def _with_related(queryset):
    return queryset.select_related('author', 'category').prefetch_related('tags')


def get_published_articles():
    return _with_related(
        Article.objects.filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )
    )


def get_breaking_articles(limit=10):
    return get_published_articles().filter(is_breaking=True)[:limit]


def get_featured_articles(limit=10):
    return get_published_articles().filter(is_featured=True)[:limit]


def search_articles(query):
    from django.db.models import Q
    return get_published_articles().filter(
        Q(title__icontains=query)
        | Q(excerpt__icontains=query)
        | Q(content__icontains=query)
        | Q(tags__name__icontains=query)
        | Q(category__name__icontains=query)
        | Q(author__name__icontains=query)
    ).distinct()


def get_related_articles(article, limit=5):
    related = get_published_articles().exclude(id=article.id)
    if article.category_id:
        related = related.filter(category_id=article.category_id)
    else:
        related = related.none()
    return related[:limit]


def get_categories_with_article_counts():
    from .models import Category
    return Category.objects.annotate(article_count=Count('articles'))


def get_tags_with_article_counts():
    from .models import Tag
    return Tag.objects.annotate(article_count=Count('articles'))
