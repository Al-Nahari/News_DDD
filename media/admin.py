from django.contrib import admin
from .models import ImageGallery, Video, MediaCategory

@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__username')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_by', 'created_at')
    search_fields = ('title', 'description', 'uploaded_by__username')
    list_filter = ('category', 'created_at')
    ordering = ('-created_at',)
