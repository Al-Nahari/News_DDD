# news_ddd/urls.py
from django.contrib import admin
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

# Legacy, read-only, unversioned endpoints kept for backward compatibility.
from news import views as legacy_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Versioned REST API — the primary API going forward.
    path('api/v1/', include('news.api.urls')),

    # GraphQL kept pending confirmation of frontend usage (see README /
    # refactor report); mutations are now permission-checked.
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema='news_ddd.schema.schema'))),

    # --- Legacy, read-only, unversioned endpoints (kept for compatibility) ---
    path('api/news/', legacy_views.ArticleListAPIView.as_view(), name='api_news_list'),
    path('api/news/<int:article_id>/', legacy_views.ArticleDetailAPIView.as_view(), name='api_news_detail'),
    path('api/breaking/', legacy_views.BreakingNewsAPIView.as_view(), name='api_breaking'),
    path('api/featured/', legacy_views.FeaturedArticlesAPIView.as_view(), name='api_featured'),
    path('api/categories/', legacy_views.CategoriesAPIView.as_view(), name='api_categories'),
    path('api/tags/', legacy_views.TagsAPIView.as_view(), name='api_tags'),
    path('api/authors/', legacy_views.AuthorsAPIView.as_view(), name='api_authors'),
    path('api/health/', legacy_views.health_check, name='api_health'),
]
