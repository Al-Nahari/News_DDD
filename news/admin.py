# news/admin.py
from django.contrib import admin

from .models import ArticleLike, AuditLog
from .models import Article, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color', 'icon')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'category', 'status', 'is_breaking',
        'is_featured', 'views', 'likes', 'published_at',
    )
    search_fields = ('title', 'content', 'excerpt', 'author__name', 'category__name')
    list_filter = ('status', 'is_breaking', 'is_featured', 'category', 'published_at')
    # autocomplete_fields avoid loading every Author/Category row into a
    # <select> — important once articles number in the thousands.
    autocomplete_fields = ('author', 'category', 'tags')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    date_hierarchy = 'created_at'
    readonly_fields = ('views', 'likes', 'comments', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author', 'category')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'actor', 'created_at')
    search_fields = ('action',)
    list_filter = ('action', 'created_at')
    autocomplete_fields = ('actor',)
    readonly_fields = ('action', 'actor', 'data', 'created_at')
    ordering = ('-created_at',)


@admin.register(ArticleLike)
class ArticleLikeAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'created_at')
    autocomplete_fields = ('article', 'user')
    ordering = ('-created_at',)
