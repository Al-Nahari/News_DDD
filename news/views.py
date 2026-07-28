# news/views.py
from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from datetime import datetime
from django.db.models import Q, Count, Sum

from accounts.models import User, Author

from .models import Article, Category, Tag, Event


# ======== REST API VIEWS ========

class ArticleListAPIView(View):
    """API View for article list - GET /api/news/"""
    
    def get(self, request):
        # Get query parameters
        category = request.GET.get('category')
        tag = request.GET.get('tag')
        author = request.GET.get('author')
        search = request.GET.get('q')
        is_breaking = request.GET.get('is_breaking')
        is_featured = request.GET.get('is_featured')
        
        articles = Article.objects.filter(published_at__lte=timezone.now())
        
        # Apply filters
        if category:
            articles = articles.filter(category__slug=category)
        if tag:
            articles = articles.filter(tags__slug=tag)
        if author:
            articles = articles.filter(author_id=author)
        if search:
            articles = articles.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search)
            )
        if is_breaking:
            articles = articles.filter(is_breaking=True)
        if is_featured:
            articles = articles.filter(is_featured=True)
        
        articles = articles.order_by('-published_at').distinct()
        
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt,
                'featured_image': article.featured_image,
                'author': {
                    'id': article.author.id,
                    'name': article.author.name,
                    'avatar': article.author.avatar,
                    'role': article.author.role
                } if article.author else None,
                'category': {
                    'id': article.category.id,
                    'name': article.category.name,
                    'slug': article.category.slug,
                    'color': article.category.color
                } if article.category else None,
                'tags': [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in article.tags.all()],
                'is_breaking': article.is_breaking,
                'is_featured': article.is_featured,
                'views': article.views,
                'likes': article.likes,
                'reading_time': article.reading_time,
                'published_at': article.published_at.isoformat() if article.published_at else None
            })
        
        return JsonResponse({'articles': data, 'count': len(data)}, status=200)


class ArticleDetailAPIView(View):
    """API View for article detail - GET /api/news/<id>/"""
    
    def get(self, request, article_id):
        try:
            article = Article.objects.get(id=article_id)
            
            # Increment views
            article.views += 1
            article.save()
            
            # Get related articles
            related_articles = Article.objects.filter(
                category=article.category
            ).exclude(id=article.id).order_by('-published_at')[:5]
            
            data = {
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt,
                'content': article.content,
                'featured_image': article.featured_image,
                'author': {
                    'id': article.author.id,
                    'name': article.author.name,
                    'avatar': article.author.avatar,
                    'bio': article.author.bio,
                    'role': article.author.role
                } if article.author else None,
                'category': {
                    'id': article.category.id,
                    'name': article.category.name,
                    'slug': article.category.slug,
                    'color': article.category.color,
                    'icon': article.category.icon
                } if article.category else None,
                'tags': [{'id': tag.id, 'name': tag.name, 'slug': tag.slug} for tag in article.tags.all()],
                'is_breaking': article.is_breaking,
                'is_featured': article.is_featured,
                'views': article.views,
                'likes': article.likes,
                'comments': article.comments,
                'reading_time': article.reading_time,
                'published_at': article.published_at.isoformat() if article.published_at else None,
                'created_at': article.created_at.isoformat(),
                'updated_at': article.updated_at.isoformat(),
                'related_articles': [{
                    'id': a.id,
                    'title': a.title,
                    'slug': a.slug,
                    'excerpt': a.excerpt,
                    'featured_image': a.featured_image
                } for a in related_articles]
            }
            
            return JsonResponse({'article': data}, status=200)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)
    
    def put(self, request, article_id):
        """Update article - PUT /api/news/<id>/"""
        try:
            import json
            data = json.loads(request.body)
            article = Article.objects.get(id=article_id)
            
            # Update fields
            for field in ['title', 'content', 'excerpt', 'featured_image', 'is_breaking', 'is_featured']:
                if field in data:
                    setattr(article, field, data[field])
            
            article.save()
            
            # Create event
            Event.objects.create(
                event_type='article_updated',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'updated_at': datetime.now().isoformat()
                }
            )
            
            return JsonResponse({'success': True, 'message': 'Article updated'}, status=200)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    def delete(self, request, article_id):
        """Delete article - DELETE /api/news/<id>/"""
        try:
            article = Article.objects.get(id=article_id)
            
            # Create event before deletion
            Event.objects.create(
                event_type='article_deleted',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'deleted_at': datetime.now().isoformat()
                }
            )
            
            article.delete()
            
            return JsonResponse({'success': True, 'message': 'Article deleted'}, status=200)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)


class CreateArticleAPIView(View):
    """API View to create article - POST /api/news/create/"""
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            
            # Required fields
            title = data.get('title')
            slug = data.get('slug')
            excerpt = data.get('excerpt')
            content = data.get('content')
            author_id = data.get('author_id')
            category_id = data.get('category_id')
            
            if not all([title, slug, excerpt, content, author_id, category_id]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Get author and category
            try:
                author = Author.objects.get(id=author_id)
                category = Category.objects.get(id=category_id)
            except (Author.DoesNotExist, Category.DoesNotExist):
                return JsonResponse({'error': 'Author or Category not found'}, status=404)
            
            # Create article
            article = Article.objects.create(
                title=title,
                slug=slug,
                excerpt=excerpt,
                content=content,
                featured_image=data.get('featured_image'),
                author=author,
                category=category,
                is_breaking=data.get('is_breaking', False),
                is_featured=data.get('is_featured', False),
                views=data.get('views', 0),
                likes=data.get('likes', 0),
                comments=data.get('comments', 0),
                reading_time=data.get('reading_time', 1),
                published_at=datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')) if data.get('published_at') else timezone.now()
            )
            
            # Add tags if provided
            if data.get('tag_ids'):
                tags = Tag.objects.filter(id__in=data['tag_ids'])
                article.tags.set(tags)
            
            # Create event
            Event.objects.create(
                event_type='article_created',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Article created successfully',
                'article_id': article.id,
                'article_slug': article.slug
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class BreakingNewsAPIView(View):
    """API View for breaking news - GET /api/breaking/"""
    
    def get(self, request):
        articles = Article.objects.filter(
            is_breaking=True,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:10]
        
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt,
                'featured_image': article.featured_image,
                'published_at': article.published_at.isoformat() if article.published_at else None
            })
        
        return JsonResponse({'breaking_news': data, 'count': len(data)}, status=200)


class FeaturedArticlesAPIView(View):
    """API View for featured articles - GET /api/featured/"""
    
    def get(self, request):
        articles = Article.objects.filter(
            is_featured=True,
            published_at__lte=timezone.now()
        ).order_by('-published_at')[:10]
        
        data = []
        for article in articles:
            data.append({
                'id': article.id,
                'title': article.title,
                'slug': article.slug,
                'excerpt': article.excerpt,
                'featured_image': article.featured_image,
                'published_at': article.published_at.isoformat() if article.published_at else None
            })
        
        return JsonResponse({'featured_articles': data, 'count': len(data)}, status=200)


class CategoriesAPIView(View):
    """API View for categories - GET /api/categories/"""
    
    def get(self, request):
        categories = Category.objects.all()
        
        data = []
        for category in categories:
            data.append({
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'color': category.color,
                'icon': category.icon,
                'article_count': category.articles.count()
            })
        
        return JsonResponse({'categories': data, 'count': len(data)}, status=200)


class TagsAPIView(View):
    """API View for tags - GET /api/tags/"""
    
    def get(self, request):
        tags = Tag.objects.all()
        
        data = []
        for tag in tags:
            data.append({
                'id': tag.id,
                'name': tag.name,
                'slug': tag.slug,
                'article_count': tag.articles.count()
            })
        
        return JsonResponse({'tags': data, 'count': len(data)}, status=200)


class UsersAPIView(View):
    """API View for Users - GET /api/users/"""
    
    def get(self, request):
        users = User.objects.all()
        
        data = []
        for user in users:
            data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'bio': user.bio,
                'role': user.role,
                'article_count': user.articles.count()
            })
        
        return JsonResponse({'users': data, 'count': len(data)}, status=200)


class StatsAPIView(View):
    """API View for statistics - GET /api/stats/"""
    
    def get(self, request):
        total_articles = Article.objects.count()
        total_users = User.objects.count()
        total_categories = Category.objects.count()
        total_tags = Tag.objects.count()
        
        breaking_news = Article.objects.filter(is_breaking=True).count()
        featured_articles = Article.objects.filter(is_featured=True).count()
        
        total_views = Article.objects.aggregate(Sum('views'))['views__sum'] or 0
        total_likes = Article.objects.aggregate(Sum('likes'))['likes__sum'] or 0
        
        # Top articles by views
        top_articles = Article.objects.order_by('-views')[:5].values('id', 'title', 'views', 'slug')
        
        # Articles by category
        articles_by_category = Category.objects.annotate(
            article_count=Count('articles')
        ).values('name', 'slug', 'article_count')
        
        # Recent events
        recent_events = Event.objects.order_by('-timestamp')[:10].values('event_type', 'data', 'timestamp')
        
        data = {
            'total_articles': total_articles,
            'total_users': total_users,
            'total_categories': total_categories,
            'total_tags': total_tags,
            'breaking_news': breaking_news,
            'featured_articles': featured_articles,
            'total_views': total_views,
            'total_likes': total_likes,
            'top_articles': list(top_articles),
            'articles_by_category': list(articles_by_category),
            'recent_events': list(recent_events)
        }
        
        return JsonResponse({'stats': data}, status=200)


class IncrementViewsAPIView(View):
    """API View to increment views - POST /api/views/increment/"""
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            article_id = data.get('article_id')
            
            if not article_id:
                return JsonResponse({'error': 'article_id is required'}, status=400)
            
            article = Article.objects.get(id=article_id)
            article.views += 1
            article.save()
            
            return JsonResponse({
                'success': True,
                'article_id': article.id,
                'views': article.views
            }, status=200)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)


class IncrementLikesAPIView(View):
    """API View to increment likes - POST /api/likes/increment/"""
    
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            article_id = data.get('article_id')
            
            if not article_id:
                return JsonResponse({'error': 'article_id is required'}, status=400)
            
            article = Article.objects.get(id=article_id)
            article.likes += 1
            article.save()
            
            return JsonResponse({
                'success': True,
                'article_id': article.id,
                'likes': article.likes
            }, status=200)
        except Article.DoesNotExist:
            return JsonResponse({'error': 'Article not found'}, status=404)


class BulkInsertDataAPIView(View):
    """API View to bulk insert mock data - POST /api/bulk-insert/"""
    
    def post(self, request):
        try:
            # Insert Users
            users_data = [
                {
                    "username": "ahmed_mohammed",
                    "email": "ahmed@news.com",
                    "password": "password123",
                    "role": "reporter",
                    "bio": "مراسل سياسي متخصص في الشؤون الدولية",
                    "phone": "+966500000001"
                },
                {
                    "username": "fatima_alatebi",
                    "email": "fatima@news.com",
                    "password": "password123",
                    "role": "editor",
                    "bio": "خبيرة اقتصادية وتحليلية",
                    "phone": "+966500000002"
                },
                {
                    "username": "khaled_alsalem",
                    "email": "khaled@news.com",
                    "password": "password123",
                    "role": "reporter",
                    "bio": "مراسل رياضي",
                    "phone": "+966500000003"
                },
                {
                    "username": "nora_alharbi",
                    "email": "nora@news.com",
                    "password": "password123",
                    "role": "editor",
                    "bio": "كاتبة ومحررة",
                    "phone": "+966500000004"
                }
            ]
            
            users = []
            for data in users_data:
                try:
                    user = User.objects.get(username=data['username'])
                    user.email = data['email']
                    user.role = data['role']
                    user.bio = data['bio']
                    user.phone = data['phone']
                    user.save()
                except User.DoesNotExist:
                    user = User.objects.create_user(**data)
                users.append(user)
            
            # Insert Categories
            categories_data = [
                {"name": "السياسة", "slug": "politics", "color": "#3B82F6", "icon": "landmark"},
                {"name": "الاقتصاد", "slug": "economy", "color": "#10B981", "icon": "chart-line"},
                {"name": "الرياضة", "slug": "sports", "color": "#F59E0B", "icon": "trophy"},
                {"name": "التقنية", "slug": "technology", "color": "#8B5CF6", "icon": "microchip"},
                {"name": "الصحة", "slug": "health", "color": "#EF4444", "icon": "heartbeat"}
            ]
            
            categories = []
            for data in categories_data:
                try:
                    category = Category.objects.get(slug=data['slug'])
                    category.name = data['name']
                    category.color = data['color']
                    category.icon = data['icon']
                    category.save()
                except Category.DoesNotExist:
                    category = Category.objects.create(**data)
                categories.append(category)
            
            # Insert Tags
            tags_data = [
                {"name": "القمة", "slug": "summit"},
                {"name": "السلام", "slug": "peace"},
                {"name": "بترول", "slug": "oil"},
                {"name": "أوبك", "slug": "opec"},
                {"name": "ذكاء اصطناعي", "slug": "ai"},
                {"name": "تقنية", "slug": "tech"},
                {"name": "صحة", "slug": "health"},
                {"name": "رياضة", "slug": "sports"},
                {"name": "لقاح", "slug": "vaccine"},
                {"name": "أسهم", "slug": "stocks"},
                {"name": "اقتصاد", "slug": "economy"}
            ]
            
            tags = []
            for data in tags_data:
                try:
                    tag = Tag.objects.get(slug=data['slug'])
                    tag.name = data['name']
                    tag.save()
                except Tag.DoesNotExist:
                    tag = Tag.objects.create(**data)
                tags.append(tag)
            
            # Insert Articles
            articles_data = [
                {
                    "title": "قمة دولية في الرياض لبحث السلام في المنطقة بمشاركة قادة من 15 دولة",
                    "slug": "international-peace-summit-riyadh",
                    "excerpt": "انطلقت اليوم القمة الدولية للسلام في العاصمة السعودية الرياض بحضور قادة دول وممثلي منظمات دولية لبحث سبل إنهاء الصراعات في المنطقة.",
                    "content": "انطلقت اليوم القمة الدولية للسلام في العاصمة السعودية الرياض بحضور قادة دول وممثلي منظمات دولية لبحث سبل إنهاء الصراعات في المنطقة. وتركز القمة على تعزيز التعاون الاقتصادي والأمني بين الدول المشاركة.",
                    "featured_image": "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=800&h=500&fit=crop",
                    "user_id": 1,
                    "category_id": 1,
                    "tag_ids": [1, 2],
                    "is_breaking": True,
                    "is_featured": True,
                    "views": 15420,
                    "likes": 1250,
                    "comments": 340,
                    "reading_time": 4,
                    "published_at": datetime.now().isoformat()
                },
                {
                    "title": "ارتفاع كبير في أسعار النفط بعد قرارات أوبك الأخيرة",
                    "slug": "oil-prices-rise-opec-decision",
                    "excerpt": "شهدت أسعار النفط ارتفاعاً ملحوظاً بعد أن أعلنت منظمة البلدان المصدرة للبترول عن خفض الإنتاج.",
                    "content": "شهدت أسعار النفط العالمية ارتفاعاً ملحوظاً بعد أن أعلنت منظمة البلدان المصدرة للبترول وحلفائها عن خفض الإنتاج بنسبة 5%. ويعزى هذا الارتفاع إلى زيادة الطلب العالمي.",
                    "featured_image": "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=800&h=500&fit=crop",
                    "user_id": 2,
                    "category_id": 2,
                    "tag_ids": [3, 4],
                    "is_breaking": False,
                    "is_featured": True,
                    "views": 8920,
                    "likes": 640,
                    "comments": 120,
                    "reading_time": 3,
                    "published_at": datetime.now().isoformat()
                },
                {
                    "title": "انطلاق فعاليات القمة العالمية للذكاء الاصطناعي في دبي",
                    "slug": "ai-summit-dubai-launch",
                    "excerpt": "انطلقت فعاليات القمة العالمية للذكاء الاصطناعي في دبي بمشاركة خبراء وشركات تقنية عالمية.",
                    "content": "انطلقت اليوم فعاليات القمة العالمية للذكاء الاصطناعي في دبي بمشاركة أكثر من 500 خبير وشركة تقنية عالمية. وتركز القمة على مستقبل الذكاء الاصطناعي وتطبيقاته.",
                    "featured_image": "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=800&h=500&fit=crop",
                    "user_id": 3,
                    "category_id": 4,
                    "tag_ids": [5, 6],
                    "is_breaking": False,
                    "is_featured": False,
                    "views": 6540,
                    "likes": 420,
                    "comments": 89,
                    "reading_time": 5,
                    "published_at": datetime.now().isoformat()
                },
                {
                    "title": "دراسة جديدة تكشف عن فوائد مذهلة للتمارين الرياضية",
                    "slug": "study-reveals-benefits-exercise",
                    "excerpt": "أظهرت دراسة جديدة أن ممارسة الرياضة بانتظام يمكن أن تزيد من العمر المتوقع.",
                    "content": "أظهرت دراسة جديدة أجريت على آلاف المشاركين أن ممارسة الرياضة بانتظام يمكن أن تزيد من العمر المتوقع بنسبة 20%. وتوصل الباحثون إلى هذه النتائج بعد متابعة المشاركين.",
                    "featured_image": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&h=500&fit=crop",
                    "user_id": 4,
                    "category_id": 3,
                    "tag_ids": [7, 8],
                    "is_breaking": False,
                    "is_featured": False,
                    "views": 4230,
                    "likes": 380,
                    "comments": 65,
                    "reading_time": 4,
                    "published_at": datetime.now().isoformat()
                },
                {
                    "title": "الكشف عن تطوير لقاح جديد لمرض خطير",
                    "slug": "new-vaccine-development",
                    "excerpt": "أعلنت شرطة دوائية رائدة عن تطوير لقاح جديد لمرض خطير يهدد ملايين الأشخاص.",
                    "content": "أعلنت شركة دوائية رائدة عن تطوير لقاح جديد لمرض خطير يهدد ملايين الأشخاص حول العالم. وأظهرت التجارب الأولية نجاحاً كبيراً.",
                    "featured_image": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&h=500&fit=crop",
                    "user_id": 2,
                    "category_id": 5,
                    "tag_ids": [9, 7],
                    "is_breaking": True,
                    "is_featured": False,
                    "views": 12300,
                    "likes": 890,
                    "comments": 210,
                    "reading_time": 3,
                    "published_at": datetime.now().isoformat()
                },
                {
                    "title": "انهيار في سوق الأسهم العالمية بسبب التوترات الاقتصادية",
                    "slug": "stock-market-crash",
                    "excerpt": "شهدت الأسواق المالية العالمية انهياراً كبيراً بسبب التوترات الاقتصادية الجيوسياسية.",
                    "content": "شهدت الأسواق المالية العالمية انهياراً كبيراً بسبب التوترات الاقتصادية الجيوسياسية. وانخفض مؤشرات الأسهم الرئيسية.",
                    "featured_image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=500&fit=crop",
                    "user_id": 2,
                    "category_id": 2,
                    "tag_ids": [10, 11],
                    "is_breaking": True,
                    "is_featured": False,
                    "views": 18900,
                    "likes": 1200,
                    "comments": 450,
                    "reading_time": 6,
                    "published_at": datetime.now().isoformat()
                }
            ]
            
            articles_created = 0
            for article_data in articles_data:
                try:
                    # Get or create Author from User
                    user = User.objects.get(id=article_data['user_id'])
                    author, created = Author.objects.get_or_create(
                        user=user,
                        defaults={
                            'name': user.username,
                            'avatar': user.avatar or '',
                            'bio': user.bio or '',
                            'role': user.role
                        }
                    )
                    
                    category = Category.objects.get(id=article_data['category_id'])
                    
                    article, created = Article.objects.get_or_create(
                        slug=article_data['slug'],
                        defaults={
                            'title': article_data['title'],
                            'excerpt': article_data['excerpt'],
                            'content': article_data['content'],
                            'featured_image': article_data['featured_image'],
                            'author': author,
                            'category': category,
                            'is_breaking': article_data['is_breaking'],
                            'is_featured': article_data['is_featured'],
                            'views': article_data['views'],
                            'likes': article_data['likes'],
                            'comments': article_data['comments'],
                            'reading_time': article_data['reading_time'],
                            'published_at': datetime.fromisoformat(article_data['published_at'].replace('Z', '+00:00'))
                        }
                    )
                    
                    if created:
                        # Add tags
                        tags_to_add = Tag.objects.filter(id__in=article_data['tag_ids'])
                        article.tags.set(tags_to_add)
                        articles_created += 1
                        
                        # Create event
                        Event.objects.create(
                            event_type='article_created',
                            data={
                                'article_id': article.id,
                                'title': article.title,
                                'slug': article.slug,
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        
                except Exception as e:
                    print(f"Error creating article {article_data['slug']}: {e}")
                    continue
            
            return JsonResponse({
                'success': True,
                'message': f"Data inserted successfully! Created: {len(users)} users, {len(categories)} categories, {len(tags)} tags, {articles_created} articles",
                'data': {
                    'users': len(users),
                    'categories': len(categories),
                    'tags': len(tags),
                    'articles': articles_created
                }
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


def health_check(request):
    """Health check endpoint - GET /api/health/"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'news-api',
        'version': '1.0.0'
    }, status=200)
