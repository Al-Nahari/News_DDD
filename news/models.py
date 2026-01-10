# news/models.py
from django.db import models
from accounts.models import User


class Category(models.Model):
    """Category Model - تصنيف المقالات"""
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, verbose_name="الرابط")
    color = models.CharField(max_length=20, default='#3B82F6', verbose_name="اللون")
    icon = models.CharField(max_length=50, default='category', verbose_name="الرمز")

    class Meta:
        db_table = 'news_category'
        verbose_name = "تصنيف"
        verbose_name_plural = "تصنيفات"

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tag Model - وسوم المقالات"""
    name = models.CharField(max_length=50, verbose_name="اسم الوسم")
    slug = models.SlugField(unique=True, verbose_name="الرابط")
    
    class Meta:
        db_table = 'news_tag'
        verbose_name = "وسم"
        verbose_name_plural = "وسوم"

    def __str__(self):
        return self.name


class Author(models.Model):
    """Author Model - مؤلف المقالات"""
    name = models.CharField(max_length=200, verbose_name="الاسم")
    avatar = models.URLField(max_length=500, verbose_name="الصورة")
    bio = models.TextField(verbose_name="السيرة الذاتية")
    role = models.CharField(max_length=50, default='reporter', verbose_name="الدور")
    
    class Meta:
        db_table = 'news_author'
        verbose_name = "مؤلف"
        verbose_name_plural = "مؤلفين"

    def __str__(self):
        return self.name


class Article(models.Model):
    """Article Model - المقالات والأخبار"""
    title = models.CharField(max_length=500, verbose_name="العنوان")
    slug = models.SlugField(unique=True, verbose_name="الرابط")
    excerpt = models.TextField(verbose_name="الملخص")
    content = models.TextField(verbose_name="المحتوى")
    featured_image = models.URLField(max_length=1000, null=True, blank=True, verbose_name="الصورة المميزة")
    
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="المؤلف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="التصنيف")
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True, verbose_name="الوسوم")
    
    is_breaking = models.BooleanField(default=False, verbose_name="خبر عاجل")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    
    views = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    likes = models.IntegerField(default=0, verbose_name="عدد الإعجابات")
    comments = models.IntegerField(default=0, verbose_name="عدد التعليقات")
    reading_time = models.IntegerField(default=1, verbose_name="وقت القراءة (دقائق)")
    
    published_at = models.DateTimeField(verbose_name="تاريخ النشر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'news_article'
        ordering = ['-published_at']
        verbose_name = "مقال"
        verbose_name_plural = "مقالات"

    def __str__(self):
        return self.title


class Event(models.Model):
    """Event Model - Event Sourcing للسجلات"""
    event_type = models.CharField(max_length=100, verbose_name="نوع الحدث")
    data = models.JSONField(verbose_name="البيانات")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="التوقيت")
    
    class Meta:
        db_table = 'news_event'
        ordering = ['-timestamp']
        verbose_name = "حدث"
        verbose_name_plural = "أحداث"

    def __str__(self):
        return f"{self.event_type} - {self.timestamp}"
