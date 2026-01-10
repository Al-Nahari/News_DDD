# news/admin.py
from django.contrib import admin
from .models import Article, Category, Tag, Author, Event


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name', 'bio')
    list_filter = ('role',)
    ordering = ('-id',)


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
    list_display = ('title', 'author', 'category', 'is_breaking', 'is_featured', 'views', 'likes', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    list_filter = ('is_breaking', 'is_featured', 'category', 'author', 'published_at')
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at', '-created_at')
    date_hierarchy = 'published_at'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'timestamp')
    search_fields = ('event_type',)
    list_filter = ('event_type', 'timestamp')
    ordering = ('-timestamp',)
    readonly_fields = ('event_type', 'data', 'timestamp')