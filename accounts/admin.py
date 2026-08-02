# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Author, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom fields are declared as their own explicit fieldsets rather than
    concatenated onto BaseUserAdmin.fieldsets — concatenating tuples that
    Django itself may restructure between versions is what produced the
    previous `/admin/accounts/user/` crash. Explicit fieldsets are immune to
    upstream layout changes."""

    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser', 'is_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-id',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'bio', 'avatar')}),
        (_('Role & permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'user')
    search_fields = ('name',)
    autocomplete_fields = ('user',)
