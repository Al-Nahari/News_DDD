# news/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone


class Category(models.Model):
    """Category Model - تصنيف المقالات"""
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف")
    slug = models.SlugField(unique=True, verbose_name="الرابط")
    # color/icon are consumed directly by the Next.js frontend to render
    # category chips without a lookup table there, so they stay on the model.
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


class Article(models.Model):
    """Article Model - المقالات والأخبار"""

    class Status(models.TextChoices):
        DRAFT = 'draft', 'مسودة'
        PENDING_REVIEW = 'pending_review', 'قيد المراجعة'
        PUBLISHED = 'published', 'منشور'
        ARCHIVED = 'archived', 'مؤرشف'

    title = models.CharField(max_length=500, verbose_name="العنوان")
    slug = models.SlugField(max_length=500, unique=True, verbose_name="الرابط")
    excerpt = models.TextField(verbose_name="الملخص")
    content = models.TextField(verbose_name="المحتوى")
    featured_image = models.URLField(max_length=1000, blank=True, null=True, verbose_name="صورة مميزة")

    author = models.ForeignKey('accounts.Author', on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="المؤلف")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='articles', verbose_name="التصنيف")
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True, verbose_name="الوسوم")

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT,
        verbose_name="حالة النشر",
    )

    is_breaking = models.BooleanField(default=False, verbose_name="خبر عاجل")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")

    # System-managed engagement counters. The API never accepts these from
    # clients directly (see news/api/serializers.py) — they are only changed
    # through dedicated, permission-checked actions/services.
    views = models.PositiveIntegerField(default=0, verbose_name="عدد المشاهدات")
    likes = models.PositiveIntegerField(default=0, verbose_name="عدد الإعجابات")
    comments = models.PositiveIntegerField(default=0, verbose_name="عدد التعليقات")
    reading_time = models.PositiveIntegerField(default=1, verbose_name="وقت القراءة (دقائق)")

    # SEO
    meta_title = models.CharField(max_length=255, blank=True, verbose_name="عنوان SEO")
    meta_description = models.CharField(max_length=500, blank=True, verbose_name="وصف SEO")

    scheduled_at = models.DateTimeField(
        null=True, blank=True, verbose_name="موعد النشر المجدول",
        help_text="اترك فارغاً للنشر الفوري عند تغيير الحالة إلى 'منشور'",
    )
    published_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ النشر")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        db_table = 'news_article'
        ordering = ['-published_at', '-created_at']
        verbose_name = "مقال"
        verbose_name_plural = "مقالات"
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['is_breaking']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return (
            self.status == self.Status.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )


class ArticleLike(models.Model):
    """Records that a specific user liked a specific article, so the same
    user can't inflate the counter by liking repeatedly."""

    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='like_records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='article_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'news_article_like'
        unique_together = ('article', 'user')

    def __str__(self):
        return f"{self.user_id} likes {self.article_id}"


class AuditLog(models.Model):
    """Lightweight audit trail for who changed what and when.

    This replaces the previous ad-hoc ``Event`` model, which was labelled
    'Event Sourcing' but was never used to reconstruct state — only to log
    actions after the fact. That's an audit log, so it's named and modeled
    as one.
    """
    action = models.CharField(max_length=100, verbose_name="الإجراء")
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_logs', verbose_name="المستخدم",
    )
    data = models.JSONField(default=dict, blank=True, verbose_name="البيانات")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="التوقيت")

    class Meta:
        db_table = 'news_audit_log'
        ordering = ['-created_at']
        verbose_name = "سجل تدقيق"
        verbose_name_plural = "سجلات التدقيق"

    def __str__(self):
        return f"{self.action} - {self.created_at}"
