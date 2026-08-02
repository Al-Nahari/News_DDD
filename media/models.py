# media/models.py
from django.db import models
from django.utils import timezone


class MediaCategory(models.Model):
    """MediaCategory Model - تصنيفات الملفات الإعلامية"""
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, verbose_name="الرابط")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    
    class Meta:
        db_table = 'media_category'
        verbose_name = "تصنيف وسائط"
        verbose_name_plural = "تصنيفات الوسائط"
    
    def __str__(self):
        return self.name


class ImageGallery(models.Model):
    """ImageGallery Model - معرض الصور"""
    title = models.CharField(max_length=255, verbose_name="العنوان")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    image_url = models.URLField(max_length=1000, verbose_name="رابط الصورة")
    
    # Relations
    category = models.ForeignKey(
        MediaCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='images',
        verbose_name="التصنيف"
    )
    uploaded_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='uploaded_images',
        verbose_name="مرفوع بواسطة"
    )
    article = models.ForeignKey(
        'news.Article', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='images',
        verbose_name="المقال المرتبط"
    )
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'media_image_gallery'
        ordering = ['-created_at']
        verbose_name = "صورة"
        verbose_name_plural = "معرض الصور"
    
    def __str__(self):
        return self.title


class Video(models.Model):
    """Video Model - الفيديوهات"""
    title = models.CharField(max_length=255, verbose_name="العنوان")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    video_url = models.URLField(max_length=1000, verbose_name="رابط الفيديو")
    thumbnail = models.URLField(max_length=1000, blank=True, null=True, verbose_name="صورة مصغرة")
    
    # Relations
    category = models.ForeignKey(
        MediaCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='videos',
        verbose_name="التصنيف"
    )
    uploaded_by = models.ForeignKey(
        'accounts.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='uploaded_videos',
        verbose_name="مرفوع بواسطة"
    )
    article = models.ForeignKey(
        'news.Article', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='videos',
        verbose_name="المقال المرتبط"
    )
    
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'media_video'
        ordering = ['-created_at']
        verbose_name = "فيديو"
        verbose_name_plural = "الفيديوهات"
    
    def __str__(self):
        return self.title
