# news/api/filters.py
import django_filters

from ..models import Article


class ArticleFilter(django_filters.FilterSet):
    category = django_filters.CharFilter(field_name='category__slug')
    tag = django_filters.CharFilter(field_name='tags__slug')
    author = django_filters.NumberFilter(field_name='author_id')
    is_breaking = django_filters.BooleanFilter()
    is_featured = django_filters.BooleanFilter()
    published_after = django_filters.IsoDateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = django_filters.IsoDateTimeFilter(field_name='published_at', lookup_expr='lte')

    class Meta:
        model = Article
        fields = ['category', 'tag', 'author', 'is_breaking', 'is_featured']
