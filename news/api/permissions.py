# news/api/permissions.py
from rest_framework.permissions import SAFE_METHODS, BasePermission

from accounts import permissions as roles


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return roles.is_admin(request.user)


class ArticlePermission(BasePermission):
    """Public read access to published articles (list/detail filtering for
    "published only" happens in the queryset, not here). Writes require a
    reporter role or above; who can edit/delete a specific article is
    resolved per-object via accounts.permissions."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return roles.can_write_articles(request.user)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'DELETE':
            return roles.can_delete_article(request.user, obj)
        return roles.can_edit_article(request.user, obj)


class CanReviewAndPublish(BasePermission):
    def has_permission(self, request, view):
        return roles.can_review_and_publish(request.user)


class CanManageTaxonomy(BasePermission):
    """Categories/tags — write access reserved for admins."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return roles.can_manage_taxonomy(request.user)
