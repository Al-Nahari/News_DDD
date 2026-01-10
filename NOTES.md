# ملاحظات المشروع - News Website API

## 📋 ملخص المشروع

هذا المشروع عبارة عن **موقع أخباري كامل** باستخدام Django و GraphQL، مصمم للربط مع تطبيق Next.js frontend. يوفر الـ API الكامل لإدارة المقالات، المؤلفين، التصنيفات، الوسوم، ويستخدم نمط Event Sourcing لتسجيل جميع الأحداث.

## 🎯 المميزات الرئيسية

### 1. نموذج بيانات متكامل
- **User**: نظام المستخدمين مع الصلاحيات
- **Author**: مؤلفو المقالات
- **Category**: تصنيفات المقالات
- **Tag**: وسوم المقالات
- **Article**: المقالات والأخبار
- **Event**: تسجيل الأحداث (Event Sourcing)

### 2. واجهات برمجة تطبيقات متعددة
- **REST API**: 15+ endpoint
- **GraphQL**: queries و mutations كاملة
- **Admin Panel**: واجهة إدارة

### 3. مميزات متقدمة
- **Event Sourcing**: تسجيل جميع الأحداث
- **CQRS**: فصل القراءة عن الكتابة
- **DDD**: تصميم Domain-Driven Design
- **Multi-language**: دعم العربية والإنجليزية

## 📊 نموذج البيانات (ERD)

```
User (AbstractUser)
├── is_editor
├── is_reporter
├── role
└── profile_picture

Author
├── name
├── avatar
├── bio
└── role

Category
├── name
├── slug (unique)
├── color
└── icon

Tag
├── name
├── slug (unique)

Article
├── title
├── slug (unique)
├── excerpt
├── content
├── featured_image
├── author (FK)
├── category (FK)
├── tags (M2M)
├── is_breaking
├── is_featured
├── views
├── likes
├── comments
├── reading_time
├── published_at
├── created_at
└── updated_at

Event
├── event_type
├── data (JSON)
└── timestamp
```

## 🔌 API Endpoints Summary

### REST API (15 endpoints)

| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/news/` | جميع المقالات + فلترة |
| POST | `/api/news/create/` | إنشاء مقال |
| GET | `/api/news/<id>/` | مقال محدد |
| PUT | `/api/news/<id>/` | تحديث مقال |
| DELETE | `/api/news/<id>/` | حذف مقال |
| GET | `/api/breaking/` | أخبار عاجلة |
| GET | `/api/featured/` | أخبار مميزة |
| GET | `/api/categories/` | جميع التصنيفات |
| GET | `/api/tags/` | جميع الوسوم |
| GET | `/api/authors/` | جميع المؤلفين |
| GET | `/api/stats/` | إحصائيات |
| POST | `/api/views/increment/` | زيادة مشاهدات |
| POST | `/api/likes/increment/` | زيادة إعجابات |
| POST | `/api/bulk-insert/` | بيانات تجريبية |
| GET | `/api/health/` | فحص النظام |

### GraphQL

**Queries (14):**
- allArticles, articleById, articleBySlug
- breakingArticles, featuredArticles, publishedArticles
- searchArticles, articlesByAuthor, articlesByCategory
- allCategories, allTags, allAuthors
- articleEvents, publishedEvents

**Mutations (10):**
- createAuthor, createCategory, createTag
- createArticle, publishArticle, updateArticle, deleteArticle
- incrementViews, incrementLikes
- bulkInsertData

## 🚀 كيفية الاستخدام

### 1. التثبيت والتشغيل
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# إنشاء migrations
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# إنشاء مستخدم admin
python manage.py createsuperuser

# تشغيل السيرفر
python manage.py runserver 8000
```

### 2. إدخال بيانات تجريبية
```bash
# عبر GraphQL
mutation { bulkInsertData { success message } }

# أو عبر REST
POST /api/bulk-insert/
```

### 3. الوصول إلى الـ API
- **REST**: `http://localhost:8000/api/`
- **GraphQL**: `http://localhost:8000/graphql/`
- **Admin**: `http://localhost:8000/admin/`

## 📝 أمثلة على الاستخدام

### جلب جميع المقالات
```bash
# REST
GET /api/news/

# GraphQL
query { allArticles { id title excerpt } }
```

### إنشاء مقال
```bash
# REST
POST /api/news/create/
Body: {
  "title": "عنوان",
  "slug": "slug-unique",
  "excerpt": "ملخص",
  "content": "محتوى",
  "author_id": 1,
  "category_id": 1,
  "published_at": "2026-01-09T20:00:00Z"
}

# GraphQL
mutation {
  createArticle(articleData: { ... }) {
    success
    message
    data
  }
}
```

### بحث
```bash
# REST
GET /api/news/?q=سلام

# GraphQL
query {
  searchArticles(query: "سلام") {
    id
    title
  }
}
```

### زيادة المشاهدات
```bash
# REST
POST /api/views/increment/
Body: {"article_id": 1}

# GraphQL
mutation {
  incrementViews(articleId: 1) {
    success
    data
  }
}
```

## 🎨 مميزات Event Sourcing

جميع الأحداث التالية يتم تسجيلها تلقائياً:

1. **article_created** - إنشاء مقال
2. **article_updated** - تحديث مقال
3. **article_published** - نشر مقال
4. **article_deleted** - حذف مقال
5. **author_created** - إنشاء مؤلف
6. **category_created** - إنشاء تصنيف
7. **tag_created** - إنشاء وسم

**استرجاع الأحداث:**
```graphql
query {
  articleEvents(articleId: 1) {
    eventType
    data
    timestamp
  }
}
```

## 🔐 ملاحظات أمنية

### للتطوير فقط
```python
# settings.py
DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
```

### للإنتاج
```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-secret-key-here'
CORS_ALLOWED_ORIGINS = ['https://your-frontend.com']
```

## 📦 المتطلبات

- Django >= 4.0
- graphene-django >= 3.0
- graphene-file-upload >= 1.0
- django-cors-headers >= 3.0

## 🗂️ هيكل الملفات

```
news_ddd/
├── manage.py
├── requirements.txt
├── README.md
├── API_DOCUMENTATION.md
├── API_EXAMPLES.md
├── SETUP.md
├── .gitignore
├── news_ddd/          # الإعدادات
│   ├── settings.py
│   ├── urls.py
│   └── schema.py
├── accounts/          # المستخدمين
│   ├── models.py
│   └── ...
├── news/              # المقالات
│   ├── models.py
│   ├── views.py
│   ├── admin.py
│   └── graphql/schema.py
└── media/             # الوسائط
    ├── models.py
    └── schema.py
```

## 🎯 نصائح للتطوير

### 1. استخدام GraphQL
GraphQL أفضل للتطبيقات المعقدة لأنه:
- يوفر تحديد الحقول المطلوبة
- يقلل من عدد الطلبات
- أكثر مرونة

### 2. استخدام REST
REST أفضل للتطبيقات البسيطة لأنه:
- أسهل في الاستخدام
- أكثر شهرة
- يدعم التخزين المؤقت

### 3. Event Sourcing
استخدم Event Sourcing عندما تحتاج:
- تتبع كامل للتغييرات
- إمكانية التراجع عن التغييرات
- سجل تدقيق كامل

### 4. CQRS
استخدم CQRS عندما تحتاج:
- فصل القراءة عن الكتابة
- تحسين الأداء
- قابلية التوسع

## 📚 مصادر إضافية

- [Django Documentation](https://docs.djangoproject.com/)
- [GraphQL Documentation](https://graphql.org/)
- [Graphene-Django Documentation](https://docs.graphene-python.org/projects/django/en/latest/)
- [Next.js Documentation](https://nextjs.org/docs)

## 🤝 تطوير مستقبلي

### ميزات يمكن إضافتها:
1. **Authentication**: JWT tokens
2. **Caching**: Redis
3. **Search**: Elasticsearch
4. **Notifications**: Email/SMS
5. **File Upload**: Cloud storage
6. **Comments System**
7. **Social Sharing**
8. **Analytics**

### تحسينات:
1. **Performance**: Database indexing
2. **Security**: Rate limiting
3. **Testing**: Unit tests
4. **Documentation**: Swagger/OpenAPI
5. **Monitoring**: Logging & metrics

## 🐛 حل المشاكل

### مشاكل شائعة:
1. **CORS errors**: تأكد من تثبيت django-cors-headers
2. **Import errors**: تأكد من بيئة الـ virtual environment
3. **Database errors**: شغّل migrations
4. **GraphQL errors**: تحقق من صحة الـ schema

### أوامر مساعدة:
```bash
# فحص المشروع
python manage.py check

# عرض migrations
python manage.py showmigrations

# rollback migration
python manage.py migrate news 0001

# shell
python manage.py shell
```

## 📞 دعم

لأي استفسار أو مساعدة:
1. راجع ملفات README.md و SETUP.md
2. تحقق من API_DOCUMENTATION.md
3. شاهد أمثلة الاستخدام في API_EXAMPLES.md

---
**تم إنشاء المشروع باستخدام DDD, CQRS, و Event Sourcing** 🚀