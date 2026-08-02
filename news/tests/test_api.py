# news/tests/test_api.py
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import Author, User
from news.models import Article, Category


class ArticleAPITests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Tech', slug='tech')
        self.reporter_user = User.objects.create_user(username='reporter', password='pw12345', role='reporter')
        self.reporter_author = Author.objects.create(name='Reporter', user=self.reporter_user)
        self.editor_user = User.objects.create_user(username='editor', password='pw12345', role='editor')

        self.published = Article.objects.create(
            title='Published', slug='published-article', excerpt='e', content='c',
            author=self.reporter_author, category=self.category,
            status=Article.Status.PUBLISHED, published_at=timezone.now(),
        )
        self.draft = Article.objects.create(
            title='Draft', slug='draft-article', excerpt='e', content='c',
            author=self.reporter_author, category=self.category,
            status=Article.Status.DRAFT,
        )

    def test_anonymous_can_list_published_articles_only(self):
        response = self.client.get('/api/v1/articles/')
        self.assertEqual(response.status_code, 200)
        slugs = [a['slug'] for a in response.data['data']['results']]
        self.assertIn('published-article', slugs)
        self.assertNotIn('draft-article', slugs)

    def test_anonymous_cannot_create_article(self):
        response = self.client.post('/api/v1/articles/', {
            'title': 'Hack', 'slug': 'hack', 'excerpt': 'e', 'content': 'c',
        })
        self.assertEqual(response.status_code, 401)

    def test_anonymous_cannot_delete_article(self):
        response = self.client.delete(f'/api/v1/articles/{self.published.slug}/')
        self.assertIn(response.status_code, (401, 403))

    def test_reporter_cannot_publish_directly(self):
        self.client.force_authenticate(self.reporter_user)
        response = self.client.post(f'/api/v1/articles/{self.draft.slug}/publish/')
        self.assertEqual(response.status_code, 403)

    def test_editor_can_publish(self):
        self.client.force_authenticate(self.editor_user)
        response = self.client.post(f'/api/v1/articles/{self.draft.slug}/publish/')
        self.assertEqual(response.status_code, 200)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.status, Article.Status.PUBLISHED)

    def test_client_cannot_set_view_or_like_counts_on_create(self):
        self.client.force_authenticate(self.reporter_user)
        response = self.client.post('/api/v1/articles/', {
            'title': 'New', 'slug': 'new-article', 'excerpt': 'e', 'content': 'c',
            'author': self.reporter_author.id, 'category': self.category.id,
            'views': 99999, 'likes': 99999,
        })
        self.assertEqual(response.status_code, 201)
        created = Article.objects.get(slug='new-article')
        self.assertEqual(created.views, 0)
        self.assertEqual(created.likes, 0)

    def test_detail_view_increments_views_atomically(self):
        initial = self.published.views
        self.client.get(f'/api/v1/articles/{self.published.slug}/')
        self.published.refresh_from_db()
        self.assertEqual(self.published.views, initial + 1)

    def test_list_is_paginated(self):
        response = self.client.get('/api/v1/articles/')
        self.assertIn('count', response.data['data'])
        self.assertIn('results', response.data['data'])


class UserAdminSmokeTests(APITestCase):
    """Regression check for the /admin/accounts/user/ crash."""

    def test_admin_user_changelist_and_change_page_load(self):
        admin = User.objects.create_superuser(username='root', password='pw12345', email='root@example.com')
        self.client.force_login(admin)
        list_response = self.client.get('/admin/accounts/user/')
        self.assertEqual(list_response.status_code, 200)
        change_response = self.client.get(f'/admin/accounts/user/{admin.id}/change/')
        self.assertEqual(change_response.status_code, 200)
