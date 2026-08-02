import graphene
from graphene_django import DjangoObjectType
from .models import ImageGallery, Video, MediaCategory
from accounts.models import User, Author


class MediaCategoryType(DjangoObjectType):
    """Media Category Type"""
    class Meta:
        model = MediaCategory
        fields = ("id", "name", "slug", "description")


class ImageGalleryType(DjangoObjectType):
    """Image Gallery Type"""
    class Meta:
        model = ImageGallery
        fields = ("id", "title", "description", "image_url", "category", "uploaded_by", "created_at", "updated_at")


class VideoType(DjangoObjectType):
    """Video Type"""
    class Meta:
        model = Video
        fields = ("id", "title", "description", "video_url", "thumbnail", "category", "uploaded_by", "created_at", "updated_at")


class Query(graphene.ObjectType):
    """Media Query"""
    
    all_media_categories = graphene.List(MediaCategoryType)
    all_images = graphene.List(ImageGalleryType)
    all_videos = graphene.List(VideoType)
    images_by_category = graphene.List(ImageGalleryType, category_slug=graphene.String(required=True))
    videos_by_category = graphene.List(VideoType, category_slug=graphene.String(required=True))
    
    def resolve_all_media_categories(self, info):
        return MediaCategory.objects.all()
    
    def resolve_all_images(self, info):
        return ImageGallery.objects.all().select_related('category', 'uploaded_by')
    
    def resolve_all_videos(self, info):
        return Video.objects.all().select_related('category', 'uploaded_by')
    
    def resolve_images_by_category(self, info, category_slug):
        try:
            category = MediaCategory.objects.get(slug=category_slug)
            return ImageGallery.objects.filter(category=category).select_related('category', 'uploaded_by')
        except MediaCategory.DoesNotExist:
            return []
    
    def resolve_videos_by_category(self, info, category_slug):
        try:
            category = MediaCategory.objects.get(slug=category_slug)
            return Video.objects.filter(category=category).select_related('category', 'uploaded_by')
        except MediaCategory.DoesNotExist:
            return []


class Mutation(graphene.ObjectType):
    """Media Mutations - Placeholder for future media mutations"""
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
