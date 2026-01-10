#!/usr/bin/env python
"""
Script لإدخال بيانات متنوعة وكثيرة إلى موقع الأخبار
يتم تشغيله باستخدام: python populate_data.py
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# إعداد Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_ddd.settings')
django.setup()

from news.models import Article, Category, Tag, Author, Event
from accounts.models import User


def clear_existing_data():
    """مسح البيانات الحالية"""
    print("🗑️  مسح البيانات الحالية...")
    Event.objects.all().delete()
    Article.objects.all().delete()
    Author.objects.all().delete()
    Category.objects.all().delete()
    Tag.objects.all().delete()
    print("✅ تم مسح البيانات القديمة\n")


def create_users():
    """إنشاء مستخدمين"""
    print("👤 إنشاء المستخدمين...")
    
    users_data = [
        {'username': 'admin', 'email': 'admin@news.com', 'is_staff': True, 'is_superuser': True, 'role': 'admin'},
        {'username': 'editor1', 'email': 'editor1@news.com', 'is_editor': True, 'role': 'editor'},
        {'username': 'editor2', 'email': 'editor2@news.com', 'is_editor': True, 'role': 'editor'},
        {'username': 'reporter1', 'email': 'reporter1@news.com', 'is_reporter': True, 'role': 'reporter'},
        {'username': 'reporter2', 'email': 'reporter2@news.com', 'is_reporter': True, 'role': 'reporter'},
        {'username': 'reader1', 'email': 'reader1@news.com', 'role': 'reader'},
        {'username': 'reader2', 'email': 'reader2@news.com', 'role': 'reader'},
    ]
    
    users = []
    for data in users_data:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            is_staff=data.get('is_staff', False),
            is_superuser=data.get('is_superuser', False),
            is_editor=data.get('is_editor', False),
            is_reporter=data.get('is_reporter', False),
            role=data['role']
        )
        users.append(user)
        print(f"  ✅ {user.username} ({user.role})")
    
    print(f"✅ تم إنشاء {len(users)} مستخدمين\n")
    return users


def create_authors():
    """إنشاء مؤلفين"""
    print("✍️  إنشاء المؤلفين...")
    
    authors_data = [
        {
            "name": "أحمد محمد العتيبي",
            "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
            "bio": "مراسل سياسي متخصص في الشؤون الدولية والقمم العالمية",
            "role": "reporter"
        },
        {
            "name": "فاطمة عبدالله الحربي",
            "avatar": "https://randomuser.me/api/portraits/women/44.jpg",
            "bio": "خبيرة اقتصادية وتحليلية markets و stocks",
            "role": "editor"
        },
        {
            "name": "خالد سالم السالم",
            "avatar": "https://randomuser.me/api/portraits/men/28.jpg",
            "bio": "مراسل رياضي متخصص في كرة القدم والدوري السعودي",
            "role": "reporter"
        },
        {
            "name": "نورا أحمد الشمري",
            "avatar": "https://randomuser.me/api/portraits/women/68.jpg",
            "bio": "كاتبة ومحررة متخصصة في الصحة والطب",
            "role": "editor"
        },
        {
            "name": "محمد علي الدوسري",
            "avatar": "https://randomuser.me/api/portraits/men/45.jpg",
            "bio": "مراسل تقني متخصص في الذكاء الاصطناعي والابتكار",
            "role": "reporter"
        },
        {
            "name": "سارة حسن النجار",
            "avatar": "https://randomuser.me/api/portraits/women/52.jpg",
            "bio": "محررة أولى متخصصة في الشؤون المحلية والمجتمع",
            "role": "editor"
        },
        {
            "name": "يوسف خالد الزهراني",
            "avatar": "https://randomuser.me/api/portraits/men/67.jpg",
            "bio": "مراسل تحقيقات متخصص في البيئة والطاقة",
            "role": "reporter"
        },
        {
            "name": "ليلى مبارك القحطاني",
            "avatar": "https://randomuser.me/api/portraits/women/33.jpg",
            "bio": "خبيرة في الشؤون التعليمية والجامعات",
            "role": "editor"
        }
    ]
    
    authors = []
    for data in authors_data:
        author = Author.objects.create(**data)
        authors.append(author)
        print(f"  ✅ {author.name}")
    
    print(f"✅ تم إنشاء {len(authors)} مؤلفين\n")
    return authors


def create_categories():
    """إنشاء تصنيفات"""
    print("📁 إنشاء التصنيفات...")
    
    categories_data = [
        {"name": "السياسة", "slug": "politics", "color": "#3B82F6", "icon": "landmark"},
        {"name": "الاقتصاد", "slug": "economy", "color": "#10B981", "icon": "chart-line"},
        {"name": "الرياضة", "slug": "sports", "color": "#F59E0B", "icon": "trophy"},
        {"name": "التقنية", "slug": "technology", "color": "#8B5CF6", "icon": "microchip"},
        {"name": "الصحة", "slug": "health", "color": "#EF4444", "icon": "heartbeat"},
        {"name": "التعليم", "slug": "education", "color": "#06B6D4", "icon": "graduation-cap"},
        {"name": "الثقافة", "slug": "culture", "color": "#EC4899", "icon": "book"},
        {"name": "المناخ", "slug": "climate", "color": "#14B8A6", "icon": "leaf"},
        {"name": "السياحة", "slug": "travel", "color": "#F97316", "icon": "plane"},
        {"name": "الترفيه", "slug": "entertainment", "color": "#A855F7", "icon": "film"}
    ]
    
    categories = []
    for data in categories_data:
        category = Category.objects.create(**data)
        categories.append(category)
        print(f"  ✅ {category.name}")
    
    print(f"✅ تم إنشاء {len(categories)} تصنيفات\n")
    return categories


def create_tags():
    """إنشاء وسوم"""
    print("🏷️  إنشاء الوسوم...")
    
    tags_data = [
        # سياسة
        {"name": "القمة", "slug": "summit"},
        {"name": "السلام", "slug": "peace"},
        {"name": "ال 대통ولة", "slug": "diplomacy"},
        {"name": "الانتخابات", "slug": "elections"},
        {"name": "البرلمان", "slug": "parliament"},
        
        # اقتصاد
        {"name": "بترول", "slug": "oil"},
        {"name": "أوبك", "slug": "opec"},
        {"name": "أسهم", "slug": "stocks"},
        {"name": "اقتصاد", "slug": "economy"},
        {"name": "عملات", "slug": "currencies"},
        {"name": "سوق", "slug": "market"},
        
        # رياضة
        {"name": "كأس", "slug": "cup"},
        {"name": "دوري", "slug": "league"},
        {"name": "منتخب", "slug": "national-team"},
        {"name": "أولمبياد", "slug": "olympics"},
        {"name": "رياضة", "slug": "sports"},
        
        # تقنية
        {"name": "ذكاء اصطناعي", "slug": "ai"},
        {"name": "تقنية", "slug": "tech"},
        {"name": "إنترنت", "slug": "internet"},
        {"name": "ذكاء", "slug": "smart"},
        {"name": "ابتكار", "slug": "innovation"},
        
        # صحة
        {"name": "صحة", "slug": "health"},
        {"name": "لقاح", "slug": "vaccine"},
        {"name": "طب", "slug": "medicine"},
        {"name": "وباء", "slug": "pandemic"},
        {"name": "مستشفى", "slug": "hospital"},
        
        # تعليم
        {"name": "جامعة", "slug": "university"},
        {"name": "طالب", "slug": "student"},
        {"name": "دراسة", "slug": "study"},
        {"name": "امتحان", "slug": "exam"},
        
        # ثقافة
        {"name": "كتاب", "slug": "book"},
        {"name": "فن", "slug": "art"},
        {"name": "موسيقى", "slug": "music"},
        {"name": "مسرح", "slug": "theater"},
        
        # مناخ
        {"name": "مناخ", "slug": "climate"},
        {"name": "بيئة", "slug": "environment"},
        {"name": "طاقة", "slug": "energy"},
        {"name": "طبيعة", "slug": "nature"},
        
        # سياحة
        {"name": "سفر", "slug": "travel"},
        {"name": "سياحة", "slug": "tourism"},
        {"name": "فنادق", "slug": "hotels"},
        
        # ترفيه
        {"name": "أفلام", "slug": "movies"},
        {"name": "موسيقى", "slug": "music"},
        {"name": "مشاهير", "slug": "celebrities"},
    ]
    
    tags = []
    for data in tags_data:
        tag = Tag.objects.create(**data)
        tags.append(tag)
        print(f"  ✅ {tag.name}")
    
    print(f"✅ تم إنشاء {len(tags)} وسوم\n")
    return tags


def create_articles(authors, categories, tags):
    """إنشاء مقالات متنوعة وكثيرة"""
    print("📰 إنشاء المقالات...")
    
    # قوائم عناوين متنوعة
    titles_politics = [
        "قمة دولية في الرياض لبحث السلام في المنطقة بمشاركة 20 دولة",
        "القمة العربية تناقش التحديات الاقتصادية والأمنية",
        "اتفاقية جديدة بين دول مجلس التعاون لتعزيز التعاون الاقتصادي",
        "القمة العالمية للسلام تبدأ أعمالها في الرياض",
        "بيان ختامي لقمة القادة يؤكد أهمية التعاون الإقليمي",
        "القمة العربية تبحث سبل تحقيق التنمية المستدامة",
        "قمة الطاقة العربية تناقش مستقبل الطاقة المتجددة",
        "القمة الاقتصادية توقع اتفاقيات بقيمة 50 مليار دولار",
    ]
    
    titles_economy = [
        "ارتفاع كبير في أسعار النفط بعد قرارات أوبك الأخيرة",
        "سوق الأسهم العالمية يغلق على ارتفاع ملحوظ",
        "الاقتصاد السعودي ينمو بنسبة 5.2% في الربع الثاني",
        "ارتفاع سعر صرف الدولار مقابل الريال",
        "البنك المركزي يخفض أسعار الفائدة",
        "شركات التكنولوجيا تحقق أرباحاً قياسية",
        "الاستثمارات الأجنبية تزيد في السوق المحلية",
        "الذهب يسجل أعلى سعر في 6 أشهر",
    ]
    
    titles_sports = [
        "المنتخب السعودي يفوز بلقب كأس العرب",
        "الدوري السعودي يحقق رقماً قياسياً في الحضور الجماهيري",
        "الهلال يتوج بلقب دوري أبطال آسيا",
        "النصر يحقق فوزاً تاريخياً في ديربي الرياض",
        "الرياضيون يشاركون في الأولمبياد العالمية",
        "بطولة الدوري تبدأ بمواجهات قوية",
        "المنتخب الأولمبي يتأهل للأولمبياد",
        "الكأس الذهبية تذهب للعملاق",
    ]
    
    titles_tech = [
        "انطلاق فعاليات القمة العالمية للذكاء الاصطناعي",
        "شركة تقنية رائدة تطلق نموذجاً جديداً للذكاء الاصطناعي",
        "الابتكار في مجال الروبوتات يغير مستقبل الصناعة",
        "السعودية تستثمر مليار دولار في التقنية",
        "الجيل الخامس من الإنترنت يصل للمنزل",
        "الذكاء الاصطناعي يدخل مجال الطب الحديث",
        "الشركات التقنية تبحث عن حلول للطاقة النظيفة",
        "الابتكار في مجال السيارات الكهربائية",
    ]
    
    titles_health = [
        "دراسة جديدة تكشف عن فوائد مذهلة للتمارين الرياضية",
        "الكشف عن تطوير لقاح جديد لمرض خطير",
        "الصحة العالمية تعلن عن اكتشاف طبي مهم",
        "الأطباء يطورون علاجاً جديداً للسرطان",
        "الوقاية من الأمراض المزمنة عبر التغذية السليمة",
        "الصحة النفسية تصبح أولوية عالمية",
        "التحقيقات تكشف عن أسرار النوم الصحي",
        "الطب الحديث يستخدم الذكاء الاصطناعي",
    ]
    
    titles_education = [
        "الجامعات السعودية تحتل مراكز متقدمة عالمياً",
        "منحة جديدة للطلاب المتفوقين",
        "التعليم عن بعد يصبح جزءاً من النظام",
        "الكليات التقنية تحقق نجاحات كبيرة",
        "الطلاب يشاركون في مسابقات عالمية",
        "الجامعات توقع اتفاقيات مع شركات عالمية",
        "التعليم الابتدائي يحصل على ميزانية ضخمة",
        "المدارس الذكية تبدأ في العمل",
    ]
    
    titles_culture = [
        "مهرجان الرياض الثقافي يبدأ فعالياته",
        "الفنان السعودي يحصل على جائزة عالمية",
        "المسرح السعودي يحقق نجاحات خارجية",
        "الكتاب الجديد يبيع آلاف النسخ",
        "المهرجان الموسيقي يجذب الآلاف",
        "التراث السعودي يحصل على اعتراف عالمي",
        "المعرض الفني يعرض أعمالاً جديدة",
        "السينما السعودية تحقق إيرادات عالية",
    ]
    
    titles_climate = [
        "السعودية تطلق مبادرة خضراء جديدة",
        "المناخ يتغير.. كيف نحمي كوكبنا؟",
        "الطاقة المتجددة تصل لـ 50% من الاستهلاك",
        "المشاريع البيئية الضخمة تبدأ العمل",
        "الحفاظ على التنوع البيولوجي",
        "التحذيرات من ارتفاع درجات الحرارة",
        "الاستثمار في الطاقة الشمسية يزيد",
        "البيئة النظيفة حق للجميع",
    ]
    
    titles_travel = [
        "السياحة في السعودية تحقق أرقاماً قياسية",
        "أجمل وجهات السفر في العالم",
        "الفنادق الفاخرة تفتتح في الرياض",
        "السياحة العلاجية تنمو بسرعة",
        "الرحلات الجوية تزيد خلال الإجازات",
        "السياحة الثقافية تجذب السياح",
        "الوجهات السياحية الجديدة",
        "السفر بالقطار يصبح أكثر راحة",
    ]
    
    titles_entertainment = [
        "مهرجان الأفلام الدولي يبدأ اليوم",
        "النجوم يشاركون في حفل توزيع الجوائز",
        "الموسيقى السعودية تصل العالمية",
        "مسلسل جديد يحقق نجاحاً كبيراً",
        "المسرح الكوميدي يجذب الجماهير",
        "الفنان الشاب يطلق ألبومه الجديد",
        "المهرجانات الموسيقية تعود بقوة",
        "السينما العربية تحقق إيرادات عالية",
    ]
    
    # جميع العناوين
    all_titles = {
        'politics': titles_politics,
        'economy': titles_economy,
        'sports': titles_sports,
        'technology': titles_tech,
        'health': titles_health,
        'education': titles_education,
        'culture': titles_culture,
        'climate': titles_climate,
        'travel': titles_travel,
        'entertainment': titles_entertainment,
    }
    
    # محتوى مقالات نموذجي
    content_template = """
    <p>هذا المقال يتناول موضوع {topic} بشكل مفصل وشامل. تم إجراء الأبحاث اللازمة لتقديم معلومات دقيقة ومحدثة للقارئ الكريم.</p>
    
    <h3>التفاصيل الرئيسية</h3>
    <p>شهد المجال تطورات ملحوظة في الآونة الأخيرة، حيث أظهرت الدراسات والتحليلات أهمية كبيرة لهذا الموضوع على المستويات المحلية والإقليمية والدولية.</p>
    
    <h3>التأثيرات والنتائج</h3>
    <p>تتوقع الخبراء أن يكون لهذا الموضوع تأثيرات إيجابية على مختلف القطاعات، خاصة في مجالات التنمية والابتكار.</p>
    
    <h3>التوصيات</h3>
    <p>يوصي المتخصصون بضرورة الاهتمام بهذا المجال والاستثمار فيه بشكل أكبر لتحقيق النتائج المرجوة.</p>
    
    <p>سيستمر هذا التطور في الأشهر القادمة، حيث تنتظر المتابعين التحديثات المستمرة في هذا المجال المهم.</p>
    """
    
    # إنشاء 100 مقال
    articles_created = 0
    total_articles = 100
    
    for i in range(total_articles):
        # اختيار فئة عشوائية
        category_slug = random.choice(list(all_titles.keys()))
        category = next(c for c in categories if c.slug == category_slug)
        
        # اختيار عنوان من الفئة
        title = random.choice(all_titles[category_slug])
        
        # إضافة رقم للعنوان لتجنب التكرار
        title = f"{title} - الجزء {i+1}"
        
        # إنشاء slug فريد
        slug = f"{category_slug}-{i+1}-{random.randint(1000, 9999)}"
        
        # ملخص
        excerpt = f"هذا المقال يتناول {title.split(' - ')[0]} بشكل شامل ومفصل. تعرف على التفاصيل الكاملة والتحليلات الحديثة."
        
        # محتوى
        content = content_template.format(topic=title.split(' - ')[0])
        
        # اختيار مؤلف عشوائي
        author = random.choice(authors)
        
        # اختيار وسوم (2-5 وسوم)
        article_tags = random.sample(tags, random.randint(2, 5))
        
        # مميزات عشوائية
        is_breaking = random.random() < 0.15  # 15% عاجل
        is_featured = random.random() < 0.20  # 20% مميز
        
        # إحصائيات عشوائية
        views = random.randint(100, 50000)
        likes = random.randint(10, 5000)
        comments = random.randint(0, 1000)
        reading_time = random.randint(2, 10)
        
        # تاريخ نشر (خلال آخر 90 يوم)
        days_ago = random.randint(0, 90)
        published_at = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        # صورة مميزة
        images = [
            "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1563986768494-4dee2763ff3f?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1531746790731-6c087fecd65a?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=500&fit=crop",
            "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&h=500&fit=crop",
        ]
        featured_image = random.choice(images)
        
        # إنشاء المقال
        article = Article.objects.create(
            title=title,
            slug=slug,
            excerpt=excerpt,
            content=content,
            featured_image=featured_image,
            author=author,
            category=category,
            is_breaking=is_breaking,
            is_featured=is_featured,
            views=views,
            likes=likes,
            comments=comments,
            reading_time=reading_time,
            published_at=published_at
        )
        
        # إضافة الوسوم
        article.tags.set(article_tags)
        
        # إنشاء حدث
        Event.objects.create(
            event_type='article_created',
            data={
                'article_id': article.id,
                'title': article.title,
                'slug': article.slug,
                'category': category.name,
                'author': author.name,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        # نشر المقال (80% من المقالات منشورة)
        if random.random() < 0.8:
            Event.objects.create(
                event_type='article_published',
                data={
                    'article_id': article.id,
                    'title': article.title,
                    'published_at': article.published_at.isoformat(),
                    'timestamp': datetime.now().isoformat()
                }
            )
        
        articles_created += 1
        
        # طباعة كل 10 مقالات
        if articles_created % 10 == 0:
            print(f"  ✅ تم إنشاء {articles_created} مقال")
    
    print(f"✅ تم إنشاء {articles_created} مقال بنجاح!\n")
    return articles_created


def create_sample_users(users):
    """إنشاء عينات من المستخدمين للربط مع المقالات"""
    print("👥 إنشاء عينات المستخدمين...")
    
    # إنشاء بعض المستخدمين الإضافيين
    sample_users = []
    for i in range(1, 6):
        user = User.objects.create_user(
            username=f'user{i}',
            email=f'user{i}@example.com',
            password='password123',
            role='reader'
        )
        sample_users.append(user)
        print(f"  ✅ {user.username}")
    
    print(f"✅ تم إنشاء {len(sample_users)} مستخدم إضافي\n")
    return users + sample_users


def print_statistics():
    """طباعة إحصائيات بعد الإدخال"""
    print("\n" + "="*60)
    print("📊 إحصائيات النظام")
    print("="*60)
    
    print(f"👤 المستخدمين: {User.objects.count()}")
    print(f"✍️  المؤلفين: {Author.objects.count()}")
    print(f"📁 التصنيفات: {Category.objects.count()}")
    print(f"🏷️  الوسوم: {Tag.objects.count()}")
    print(f"📰 المقالات: {Article.objects.count()}")
    print(f"📋 الأحداث: {Event.objects.count()}")
    
    print("\n📊 توزيع المقالات حسب التصنيف:")
    for category in Category.objects.all():
        count = category.articles.count()
        print(f"  {category.name}: {count} مقال")
    
    print("\n📊 المقالات المميزة:")
    print(f"  عاجلة: {Article.objects.filter(is_breaking=True).count()}")
    print(f"  مميزة: {Article.objects.filter(is_featured=True).count()}")
    
    print("\n📊 إحصائيات إضافية:")
    total_views = Article.objects.aggregate(sum='views')['sum'] or 0
    total_likes = Article.objects.aggregate(sum='likes')['sum'] or 0
    print(f"  إجمالي المشاهدات: {total_views:,}")
    print(f"  إجمالي الإعجابات: {total_likes:,}")
    
    print("\n" + "="*60)
    print("✅ تم إدخال جميع البيانات بنجاح!")
    print("="*60)


def main():
    """الدالة الرئيسية"""
    print("\n" + "="*60)
    print("🚀 بدء إدخال البيانات إلى الموقع")
    print("="*60 + "\n")
    
    try:
        # 1. مسح البيانات الحالية
        clear_existing_data()
        
        # 2. إنشاء المستخدمين
        users = create_users()
        
        # 3. إنشاء المؤلفين
        authors = create_authors()
        
        # 4. إنشاء التصنيفات
        categories = create_categories()
        
        # 5. إنشاء الوسوم
        tags = create_tags()
        
        # 6. إنشاء المقالات
        articles_count = create_articles(authors, categories, tags)
        
        # 7. إنشاء عينات مستخدمين
        all_users = create_sample_users(users)
        
        # 8. طباعة الإحصائيات
        print_statistics()
        
        print("\n🎉 تهانينا! تم إدخال جميع البيانات بنجاح!")
        print("\n💡 نصائح:")
        print("  • اذهب إلى http://localhost:8000/graphql/ لتجربة GraphQL")
        print("  • اذهب إلى http://localhost:8000/api/news/ لتجربة REST API")
        print("  • اذهب إلى http://localhost:8000/admin/ لعرض البيانات")
        print("  • اسم المستخدم: admin")
        print("  • كلمة المرور: password123")
        
    except Exception as e:
        print(f"\n❌ حدث خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()