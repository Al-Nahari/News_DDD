from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """User Model - المستخدمون مع الأدوار والصلاحيات"""
    
    ROLE_CHOICES = [
        ('admin', 'مدير'),
        ('editor', 'محرر'),
        ('reporter', 'مراسل'),
        ('reader', 'قارئ'),
    ]
    
    # `role` is the single source of truth for what a user can do — it used
    # to be duplicated with is_editor/is_reporter booleans that could drift
    # out of sync with it (e.g. role='admin' but is_editor=False). Role-based
    # checks live in accounts/permissions.py.
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='reader',
        verbose_name="الدور"
    )
    
    bio = models.TextField(blank=True, null=True, verbose_name="السيرة الذاتية")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="رقم الهاتف")
    avatar = models.URLField(blank=True, null=True, verbose_name="صورة الملف الشخصي")

    class Meta:
        db_table = 'accounts_user'
        verbose_name = "مستخدم"
        verbose_name_plural = "مستخدمون"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Author(models.Model):
    """Author Model - المؤلفون والكتاب"""
    
    name = models.CharField(max_length=200, verbose_name="الاسم")
    avatar = models.URLField(blank=True, null=True, verbose_name="صورة المؤلف")
    bio = models.TextField(blank=True, null=True, verbose_name="السيرة الذاتية")
    role = models.CharField(max_length=20, default='reporter', verbose_name="الدور")
    
    # Relation to User (optional - for authenticated users)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='author_profiles',
        verbose_name="المستخدم المرتبط"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    
    class Meta:
        db_table = 'accounts_author'
        verbose_name = "مؤلف"
        verbose_name_plural = "مؤلفون"
    
    def __str__(self):
        return self.name
