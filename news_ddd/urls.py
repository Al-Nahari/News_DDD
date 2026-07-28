# news_ddd/urls.py
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

# Import API views
from news import views as news_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # GraphQL API
    path('graphql/', csrf_exempt(GraphQLView.as_view(graphiql=True, schema='news_ddd.schema.schema'))),
    
    # REST API Endpoints
    # Articles
    path('api/news/', news_views.ArticleListAPIView.as_view(), name='api_news_list'),
    path('api/news/create/', news_views.CreateArticleAPIView.as_view(), name='api_news_create'),
    path('api/news/<int:article_id>/', news_views.ArticleDetailAPIView.as_view(), name='api_news_detail'),
    
    # Special lists
    path('api/breaking/', news_views.BreakingNewsAPIView.as_view(), name='api_breaking'),
    path('api/featured/', news_views.FeaturedArticlesAPIView.as_view(), name='api_featured'),
    
    # Metadata
    path('api/categories/', news_views.CategoriesAPIView.as_view(), name='api_categories'),
    path('api/tags/', news_views.TagsAPIView.as_view(), name='api_tags'),
    path('api/authors/', news_views.AuthorsAPIView.as_view(), name='api_authors'),
    path('api/Users/', news_views.UsersAPIView.as_view(), name='api_Users'),
    path('api/users/', news_views.UsersAPIView.as_view(), name='api_users_lower'),
    
    # Statistics
    path('api/stats/', news_views.StatsAPIView.as_view(), name='api_stats'),
    
    # Actions
    path('api/views/increment/', news_views.IncrementViewsAPIView.as_view(), name='api_increment_views'),
    path('api/likes/increment/', news_views.IncrementLikesAPIView.as_view(), name='api_increment_likes'),
    
    # Bulk operations
    path('api/bulk-insert/', news_views.BulkInsertDataAPIView.as_view(), name='api_bulk_insert'),
    
    # Health check
    path('api/health/', news_views.health_check, name='api_health'),
]
