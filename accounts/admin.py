from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_editor', 'is_reporter')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'bio', 'avatar', 'is_editor', 'is_reporter')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'phone', 'bio', 'avatar', 'is_editor', 'is_reporter')
        }),
    )
    ordering = ('-id',)

