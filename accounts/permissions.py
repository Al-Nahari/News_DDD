# accounts/permissions.py
"""Role checks shared between the REST API, GraphQL, and the admin.

Keeping this logic in one place means "can this user publish an article?"
is answered the same way everywhere instead of being re-implemented per view.
"""


def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.role == 'admin')


def is_editor(user):
    return user.is_authenticated and (is_admin(user) or user.role == 'editor')


def is_reporter(user):
    return user.is_authenticated and (is_editor(user) or user.role == 'reporter')


def can_manage_users(user):
    return is_admin(user)


def can_manage_taxonomy(user):
    """Categories, tags — content structure, not individual articles."""
    return is_admin(user)


def can_review_and_publish(user):
    return is_editor(user)


def can_write_articles(user):
    """Reporters can create/edit their own drafts; editors+ can do more."""
    return is_reporter(user)


def can_edit_article(user, article):
    if is_editor(user):
        return True
    if is_reporter(user):
        return article.author_id is not None and getattr(article.author, 'user_id', None) == user.id
    return False


def can_delete_article(user, article):
    # Deleting is destructive and reserved for editors/admins, even for a
    # reporter's own article — a reporter can archive their own work instead.
    return is_editor(user)
