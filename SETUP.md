# Setup Instructions - News Website API

دليل تثبيت وتشغيل المشروع بالكامل

## المتطلبات المسبقة

- Python 3.8 أو أعلى
- pip (مدير حزم Python)
- Git (اختياري)

## خطوات التثبيت

### 1. تنزيل المشروع

```bash
# إذا كنت تستخدم Git
git clone <your-repo-url>
cd news_ddd

# أو إذا كان الملفات مضغوطة، استخرجها وافتح الـ terminal في المجلد
```

### 2. إنشاء بيئة افتراضية

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. تثبيت المتطلبات

```bash
pip install -r requirements.txt
```

**المتطلبات التي سيتم تثبيتها:**
- Django >=4.0,<5.0
- graphene-django >=3.0,<4.0
- graphene-file-upload >=1.0,<2.0
- django-cors-headers >=3.0,<4.0

### 4. إنشاء قاعدة البيانات

```bash
# إنشاء ملفات migrations
python manage.py makemigrations

# تطبيق migrations على قاعدة البيانات
python manage.py migrate
```

### 5. إنشاء مستخدم Admin

```bash
python manage.py createsuperuser
```

سيطلب منك:
- Username: (اختر اسم مستخدم)
- Email: (اختياري)
- Password: (اختر كلمة مرور)

### 6. تشغيل السيرفر

```bash
python manage.py runserver 8000
```

السيرفر سيعمل على: `http://localhost:8000`

## اختبار المشروع

### 1. إدخال بيانات تجريبية

يمكنك إدخال بيانات تجريبية بثلاث طرق:

**الطريقة 1: عبر GraphQL Playground**
1. افتح: `http://localhost:8000/graphql/`
2. اكتب هذا الـ Query:
```graphql
mutation {
  bulkInsertData {
    success
    message
    data
  }
}
```
3. اضغط Play

**الطريقة 2: عبر REST API**
```bash
curl -X POST http://localhost:8000/api/bulk-insert/
```

**الطريقة 3: عبر Admin Panel**
- اذهب إلى: `http://localhost:8000/admin/`
- سجل الدخول باستخدام بيانات الـ superuser
- أضف البيانات يدوياً

### 2. اختبار الـ API

#### REST API
```bash
# جميع المقالات
curl http://localhost:8000/api/news/

# مقال محدد
curl http://localhost:8000/api/news/1/

# أخبار عاجلة
curl http://localhost:8000/api/breaking/

# إحصائيات
curl http://localhost:8000/api/stats/

# فحص النظام
curl http://localhost:8000/api/health/
```

#### GraphQL
افتح في المتصفح: `http://localhost:8000/graphql/`

**مثال على Query:**
```graphql
query {
  allArticles {
    id
    title
    excerpt
    author {
      name
    }
    category {
      name
      color
    }
  }
}
```

**مثال على Mutation:**
```graphql
mutation {
  createArticle(articleData: {
    title: "مقال تجريبي",
    slug: "test-article",
    excerpt: "هذا مقال تجريبي",
    content: "محتوى المقال التجريبي",
    authorId: 1,
    categoryId: 1,
    publishedAt: "2026-01-09T20:00:00Z"
  }) {
    success
    message
    data
  }
}
```

### 3. Admin Panel

اذهب إلى: `http://localhost:8000/admin/`

يمكنك:
- إدارة المقالات
- إدارة المؤلفين
- إدارة التصنيفات
- إدارة الوسوم
- عرض الأحداث

## إعدادات Next.js Frontend

إذا كنت تستخدم Next.js، إليك الخطوات:

### 1. إنشاء مشروع Next.js

```bash
npx create-next-app@latest news-frontend
cd news-frontend
```

### 2. إعداد الـ API Client

أنشئ ملف `lib/api.ts` وأضف الكود من ملف `API_EXAMPLES.md`

### 3. تشغيل Next.js

```bash
npm run dev
```

سيعمل على: `http://localhost:3000`

### 4. ملاحظات هامة

**CORS Settings:**
إذا واجهت مشاكل CORS، أضف هذا إلى `news_ddd/settings.py`:

```python
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # في بداية القائمة
    # ... rest of middleware
]

CORS_ALLOW_ALL_ORIGINS = True  # للتطوير فقط
# أو
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

**تثبيت CORS:**
```bash
pip install django-cors-headers
```

## هيكل المشروع

```
news_ddd/
├── manage.py
├── requirements.txt
├── README.md
├── API_DOCUMENTATION.md
├── API_EXAMPLES.md
├── SETUP.md
├── .gitignore
├── db.sqlite3
├── news_ddd/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── schema.py
├── accounts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   └── migrations/
├── news/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── tests.py
│   ├── graphql/
│   │   └── schema.py
│   └── migrations/
├── media/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── schema.py
│   ├── views.py
│   ├── tests.py
│   └── migrations/
└── README.md
```

## أوامر مفيدة

### إنشاء تطبيق جديد
```bash
python manage.py startapp myapp
```

### إنشاء migrations بعد تعديل نماذج
```bash
python manage.py makemigrations
python manage.py migrate
```

### فحص صحة المشروع
```bash
python manage.py check
```

### إنشاء نسخة احتياطية من قاعدة البيانات
```bash
python manage.py dumpdata > backup.json
```

### تحميل نسخة احتياطية
```bash
python manage.py loaddata backup.json
```

### تشغيل سيرفر على منفذ معين
```bash
python manage.py runserver 0.0.0.0:8000
```

## مشاكل شائعة وإصلاحاتها

### Problem: "ModuleNotFoundError: No module named 'graphene'"
**Solution:** `pip install graphene-django`

### Problem: "Port 8000 already in use"
**Solution:** `python manage.py runserver 8001`

### Problem: "Database locked"
**Solution:** احذف `db.sqlite3` وشغّل `python manage.py migrate` مرة أخرى

### Problem: "Import errors"
**Solution:** تأكد من أنك في بيئة الـ virtual environment

### Problem: "CORS errors"
**Solution:** تأكد من تثبيت `django-cors-headers` وإضافته إلى `INSTALLED_APPS`

## اختبار الاتصال بقاعدة البيانات

```bash
python manage.py shell
```

في الـ shell:
```python
from news.models import Article
Article.objects.count()
```

إذا ظهر رقم، فالاتصال يعمل بشكل صحيح.

## نصائح للتطوير

1. **استخدم بيئة افتراضية دائماً**
2. **احفظ المتطلبات**: `pip freeze > requirements.txt`
3. **استخدم Git للتحكم في الإصدارات**
4. **اختبار الـ API قبل الربط مع Frontend**
5. **تحقق من صحة البيانات في Admin Panel**

## الخطوات التالية

بعد تشغيل المشروع بنجاح:

1. ✅ اختبار جميع الـ API endpoints
2. ✅ إدخال بيانات تجريبية
3. ✅ اختبار GraphQL Playground
4. ✅ فحص Admin Panel
5. ✅ الربط مع Next.js Frontend
6. ✅ إضافة ميزات جديدة حسب الحاجة

## دعم فني

إذا واجهت أي مشاكل:
1. تأكد من أن Python صحيح الإصدار
2. تأكد من تثبيت جميع المتطلبات
3. تأكد من تشغيل migrations
4. تحقق من logs السيرفر
5. راجع ملف README.md للتفاصيل الإضافية

---
**جاهز للتشغيل!** 🚀