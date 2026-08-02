# news/management/commands/seed_news.py
"""Development seed data.

Replaces populate_data.py / ac.py, which were plain scripts with a
hardcoded `password123` for every demo account and were reachable as a
bulk-insert HTTP endpoint. This command:
  * only ever runs from the CLI (never exposed over HTTP),
  * requires an explicit --password (or $SEED_PASSWORD) instead of a
    hardcoded default, and
  * refuses to run when DEBUG is False, so it can't be run by accident
    against a production database.

Usage:
    python manage.py seed_news --password "SomeLocalDevPassword!23"
"""
import os
import random
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import Author, User
from news.models import Article, Category, Tag

CATEGORIES = [
    {"name": "السياسة", "slug": "politics", "color": "#3B82F6", "icon": "landmark"},
    {"name": "الاقتصاد", "slug": "economy", "color": "#10B981", "icon": "chart-line"},
    {"name": "الرياضة", "slug": "sports", "color": "#F59E0B", "icon": "trophy"},
    {"name": "التقنية", "slug": "technology", "color": "#8B5CF6", "icon": "microchip"},
    {"name": "الصحة", "slug": "health", "color": "#EF4444", "icon": "heartbeat"},
]

TAGS = [
    {"name": "القمة", "slug": "summit"}, {"name": "بترول", "slug": "oil"},
    {"name": "رياضة", "slug": "sports"}, {"name": "ذكاء اصطناعي", "slug": "ai"},
    {"name": "صحة", "slug": "health"}, {"name": "اقتصاد", "slug": "economy"},
]

DEMO_USERS = [
    {"username": "demo_admin", "email": "admin@example.com", "role": "admin", "is_staff": True, "is_superuser": True},
    {"username": "demo_editor", "email": "editor@example.com", "role": "editor"},
    {"username": "demo_reporter", "email": "reporter@example.com", "role": "reporter"},
]

SAMPLE_TITLES = [
    "قمة دولية لبحث التعاون الاقتصادي بين الدول المشاركة",
    "ارتفاع ملحوظ في الأسواق العالمية بعد بيانات اقتصادية إيجابية",
    "انطلاق بطولة رياضية كبرى بمشاركة عدة منتخبات",
    "إطلاق منصة تقنية جديدة تعتمد على الذكاء الاصطناعي",
    "دراسة طبية جديدة تسلط الضوء على نمط حياة صحي",
]


class Command(BaseCommand):
    help = "Seed development data: demo users, authors, categories, tags, and articles."

    def add_arguments(self, parser):
        parser.add_argument(
            '--password', default=os.environ.get('SEED_PASSWORD'),
            help='Password for all demo accounts. Falls back to $SEED_PASSWORD.',
        )
        parser.add_argument('--articles', type=int, default=15, help='Number of sample articles to create.')

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_news refuses to run with DEBUG=False (production safeguard).")

        password = options['password']
        if not password:
            raise CommandError("Provide --password or set $SEED_PASSWORD (no hardcoded default is used).")

        categories = [Category.objects.get_or_create(slug=c['slug'], defaults=c)[0] for c in CATEGORIES]
        tags = [Tag.objects.get_or_create(slug=t['slug'], defaults=t)[0] for t in TAGS]

        authors = []
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={'email': data['email'], 'role': data['role'],
                          'is_staff': data.get('is_staff', False), 'is_superuser': data.get('is_superuser', False)},
            )
            if created:
                user.set_password(password)
                user.save()
            author, _created = Author.objects.get_or_create(
                user=user, defaults={'name': user.username, 'role': data['role']},
            )
            authors.append(author)
            self.stdout.write(self.style.SUCCESS(f"  user/author ready: {user.username} ({data['role']})"))

        created_count = 0
        for i in range(options['articles']):
            title = random.choice(SAMPLE_TITLES)
            slug = f"{title[:20]}-{i}".replace(' ', '-')
            article, created = Article.objects.get_or_create(
                slug=slug,
                defaults={
                    'title': title,
                    'excerpt': title,
                    'content': f"{title}. " * 20,
                    'author': random.choice(authors),
                    'category': random.choice(categories),
                    'status': Article.Status.PUBLISHED,
                    'published_at': timezone.now() - timedelta(days=random.randint(0, 30)),
                    'is_breaking': random.random() < 0.15,
                    'is_featured': random.random() < 0.25,
                    'reading_time': random.randint(2, 6),
                },
            )
            if created:
                article.tags.set(random.sample(tags, k=min(2, len(tags))))
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(categories)} categories, {len(tags)} tags, "
            f"{len(authors)} demo users/authors, {created_count} new articles."
        ))
