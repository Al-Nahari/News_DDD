# news/tests/test_services.py
from django.test import TestCase
from django.utils import timezone

from accounts.models import Author, User
from news.models import Article, Category
from news.services import DomainError, archive_article, increment_article_view, like_article, publish_article


class ArticleServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reporter1', password='x', role='reporter')
        self.author = Author.objects.create(name='Reporter One', user=self.user)
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.article = Article.objects.create(
            title='Test', slug='test-article', excerpt='e', content='c',
            author=self.author, category=self.category,
        )

    def test_publish_sets_status_and_timestamp(self):
        publish_article(self.article, self.user)
        self.article.refresh_from_db()
        self.assertEqual(self.article.status, Article.Status.PUBLISHED)
        self.assertIsNotNone(self.article.published_at)

    def test_cannot_republish_archived_article_directly(self):
        publish_article(self.article, self.user)
        archive_article(self.article, self.user)
        with self.assertRaises(DomainError):
            publish_article(self.article, self.user)

    def test_archiving_clears_featured_and_breaking(self):
        publish_article(self.article, self.user)
        self.article.is_featured = True
        self.article.is_breaking = True
        self.article.save()
        archive_article(self.article, self.user)
        self.article.refresh_from_db()
        self.assertFalse(self.article.is_featured)
        self.assertFalse(self.article.is_breaking)

    def test_increment_view_is_atomic_and_cumulative(self):
        for _ in range(5):
            increment_article_view(self.article)
        self.article.refresh_from_db()
        self.assertEqual(self.article.views, 5)

    def test_like_article_is_idempotent_per_user(self):
        created, count = like_article(self.article, self.user)
        self.assertTrue(created)
        self.assertEqual(count, 1)
        created_again, count_again = like_article(self.article, self.user)
        self.assertFalse(created_again)
        self.assertEqual(count_again, 1)
