# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """User Model - مستخدمي النظام مع الصلاحيات"""
    is_editor = models.BooleanField(default=False, verbose_name="محرر")
    is_reporter = models.BooleanField(default=False, verbose_name="مراسل")
    role = models.CharField(max_length=50, default='reader', verbose_name="الدور")
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True, verbose_name="صورة الملف الشخصي")
    phone = models.CharField(max_length=20, blank=True, verbose_name="الهاتف")
    bio = models.TextField(blank=True, verbose_name="السيرة الذاتية")
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = "مستخدم"
        verbose_name_plural = "مستخدمين"
    
    def __str__(self):
        return self.username or self.email or "User"
    
    @property
    def is_admin(self):
        return self.is_superuser or self.is_staff
    
    @property
    def can_edit(self):
        return self.is_editor or self.is_admin
    
    @property
    def can_report(self):
        return self.is_reporter or self.is_editor or self.is_admin
