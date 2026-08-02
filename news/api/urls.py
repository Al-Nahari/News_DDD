# news/api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register('articles', views.ArticleViewSet, basename='article')
router.register('categories', views.CategoryViewSet, basename='category')
router.register('tags', views.TagViewSet, basename='tag')
router.register('authors', views.AuthorViewSet, basename='author')

urlpatterns = [
    path('breaking/', views.breaking_news, name='v1-breaking'),
    path('featured/', views.featured_news, name='v1-featured'),
    path('health/', views.health_check, name='v1-health'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
