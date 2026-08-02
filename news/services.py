# news/services.py
"""Operations with real business logic behind them.

Simple CRUD stays in serializers/viewsets. Anything that enforces a domain
rule (you can't feature an archived article, views must increment
atomically, etc.) lives here so REST, GraphQL, and management commands all
go through the same rule instead of each re-implementing it.
"""
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Article, ArticleLike, AuditLog


class DomainError(Exception):
    """Raised when an action violates a publishing/domain rule."""


def _log(action, actor, **data):
    AuditLog.objects.create(action=action, actor=actor if getattr(actor, 'is_authenticated', False) else None, data=data)


def submit_for_review(article: Article, actor) -> Article:
    if article.status != Article.Status.DRAFT:
        raise DomainError("Only draft articles can be submitted for review.")
    article.status = Article.Status.PENDING_REVIEW
    article.save(update_fields=['status', 'updated_at'])
    _log('article_submitted_for_review', actor, article_id=article.id)
    return article


def publish_article(article: Article, actor, when=None) -> Article:
    if article.status == Article.Status.ARCHIVED:
        raise DomainError("An archived article must be restored to draft before it can be published again.")
    article.status = Article.Status.PUBLISHED
    article.published_at = when or timezone.now()
    article.save(update_fields=['status', 'published_at', 'updated_at'])
    _log('article_published', actor, article_id=article.id)
    return article


def archive_article(article: Article, actor) -> Article:
    # Archiving also un-features/un-breaks the article — an archived story
    # should never keep showing up as "featured" or "breaking".
    article.status = Article.Status.ARCHIVED
    article.is_featured = False
    article.is_breaking = False
    article.save(update_fields=['status', 'is_featured', 'is_breaking', 'updated_at'])
    _log('article_archived', actor, article_id=article.id)
    return article


def feature_article(article: Article, actor) -> Article:
    if article.status != Article.Status.PUBLISHED:
        raise DomainError("Only a published article can be marked as featured.")
    article.is_featured = True
    article.save(update_fields=['is_featured', 'updated_at'])
    _log('article_featured', actor, article_id=article.id)
    return article


@transaction.atomic
def increment_article_view(article: Article) -> None:
    # F() expression keeps this a single atomic UPDATE, avoiding lost updates
    # when many requests hit the same article concurrently.
    Article.objects.filter(pk=article.pk).update(views=F('views') + 1)


def like_article(article: Article, user) -> tuple[bool, int]:
    """Returns (created, current_like_count). A user can only like once."""
    with transaction.atomic():
        _, created = ArticleLike.objects.get_or_create(article=article, user=user)
        if created:
            Article.objects.filter(pk=article.pk).update(likes=F('likes') + 1)
    article.refresh_from_db(fields=['likes'])
    return created, article.likes
