# News Website API - Django & GraphQL

موقع أخباري كامل باستخدام Django و GraphQL مع دعم REST API، مصمم للربط مع تطبيق Next.js frontend.

## 🚀 المميزات

- **GraphQL API**: واجهة برمجة تطبيقات كاملة باستخدام GraphQL
- **REST API**: واجهة RESTful للتكامل مع أي frontend
- **Event Sourcing**: تسجيل جميع الأحداث في النظام
- **DDD Pattern**: تصميم Domain-Driven Design
- **CQRS**: فصل القراءة عن الكتابة
- **Multi-language Support**: العربية والإنجليزية

## 📊 نموذج البيانات (Data Models)

### 1. المستخدم (User)
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "is_editor": true,
  "is_reporter": false,
  "role": "editor",
  "profile_picture": "url/to/image.jpg",
  "phone": "+966500000000",
  "bio": "نصير حقوق الإنسان"
}
```

### 2. المؤلف (Author)
```json
{
  "id": 1,
  "name": "أحمد محمد",
  "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
  "bio": "مراسل سياسي متخصص في الشؤون الدولية",
  "role": "reporter"
}
```

### 3. التصنيف (Category)
```json
{
  "id": 1,
  "name": "السياسة",
  "slug": "politics",
  "color": "#3B82F6",
  "icon": "landmark"
}
```

### 4. الوسم (Tag)
```json
{
  "id": 1,
  "name": "القمة",
  "slug": "summit"
}
```

### 5. المقال/الخبر (Article)
```json
{
  "id": 1,
  "title": "قمة دولية في الرياض لبحث السلام",
  "slug": "international-peace-summit-riyadh",
  "excerpt": "انطلقت اليوم القمة الدولية للسلام...",
  "content": "<html content>",
  "featured_image": "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=800&h=500&fit=crop",
  "author": {
    "id": 1,
    "name": "أحمد محمد",
    "avatar": "https://randomuser.me/api/portraits/men/32.jpg"
  },
  "category": {
    "id": 1,
    "name": "السياسة",
    "slug": "politics",
    "color": "#3B82F6"
  },
  "tags": [
    {"id": 1, "name": "القمة", "slug": "summit"},
    {"id": 2, "name": "السلام", "slug": "peace"}
  ],
  "is_breaking": true,
  "is_featured": true,
  "views": 15420,
  "likes": 1250,
  "comments": 340,
  "reading_time": 4,
  "published_at": "2026-01-09T20:21:00+03:00",
  "created_at": "2026-01-09T20:21:00+03:00",
  "updated_at": "2026-01-09T20:21:00+03:00"
}
```

### 6. الحدث (Event) - Event Sourcing
```json
{
  "event_type": "article_created",
  "data": {
    "article_id": 1,
    "title": "قمة دولية في الرياض",
    "slug": "international-peace-summit-riyadh",
    "timestamp": "2026-01-09T20:21:00+03:00"
  },
  "timestamp": "2026-01-09T20:21:00+03:00"
}
```

## 🔌 REST API Endpoints

### المقالات والأخبار

| Method | Endpoint | الوصف | Parameters |
|--------|----------|-------|------------|
| GET | `/api/news/` | جميع المقالات | `?category=politics&tag=summit&author=1&q=بحث&is_breaking=true&is_featured=true` |
| POST | `/api/news/create/` | إنشاء مقال جديد | JSON body |
| GET | `/api/news/<id>/` | مقال محدد | - |
| PUT | `/api/news/<id>/` | تحديث مقال | JSON body |
| DELETE | `/api/news/<id>/` | حذف مقال | - |
| GET | `/api/breaking/` | أخبار عاجلة | - |
| GET | `/api/featured/` | أخبار مميزة | - |

### البيانات المرتبطة

| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/categories/` | جميع التصنيفات |
| GET | `/api/tags/` | جميع الوسوم |
| GET | `/api/authors/` | جميع المؤلفين |

### الإحصائيات

| Method | Endpoint | الوصف |
|--------|----------|-------|
| GET | `/api/stats/` | إحصائيات عامة |

### الإجراءات

| Method | Endpoint | الوصف | Body |
|--------|----------|-------|------|
| POST | `/api/views/increment/` | زيادة المشاهدات | `{"article_id": 1}` |
| POST | `/api/likes/increment/` | زيادة الإعجابات | `{"article_id": 1}` |
| POST | `/api/bulk-insert/` | إدخال بيانات تجريبية | - |
| GET | `/api/health/` | فحص النظام | - |

## 🔄 GraphQL API

### Endpoint
```
POST /graphql/
```

### Queries (قراءة البيانات)

#### جميع المقالات
```graphql
query {
  allArticles {
    id
    title
    slug
    excerpt
    featuredImage
    author {
      id
      name
      avatar
    }
    category {
      id
      name
      slug
      color
    }
    tags {
      id
      name
      slug
    }
    isBreaking
    isFeatured
    views
    likes
    readingTime
    publishedAt
  }
}
```

#### مقال محدد
```graphql
query {
  articleBySlug(slug: "international-peace-summit-riyadh") {
    id
    title
    content
    author {
      name
      avatar
      bio
    }
    category {
      name
      color
    }
    tags {
      name
    }
    views
    likes
  }
}
```

#### بحث
```graphql
query {
  searchArticles(query: "سلام") {
    id
    title
    excerpt
  }
}
```

#### أخبار عاجلة
```graphql
query {
  breakingArticles {
    id
    title
    excerpt
    featuredImage
  }
}
```

#### جميع التصنيفات
```graphql
query {
  allCategories {
    id
    name
    slug
    color
    icon
  }
}
```

### Mutations (تعديل البيانات)

#### إنشاء مؤلف
```graphql
mutation {
  createAuthor(authorData: {
    name: "خالد السالم",
    avatar: "https://randomuser.me/api/portraits/men/28.jpg",
    bio: "مراسل رياضي",
    role: "reporter"
  }) {
    success
    message
    data
  }
}
```

#### إنشاء تصنيف
```graphql
mutation {
  createCategory(categoryData: {
    name: "الرياضة",
    slug: "sports",
    color: "#F59E0B",
    icon: "trophy"
  }) {
    success
    message
    data
  }
}
```

#### إنشاء وسم
```graphql
mutation {
  createTag(tagData: {
    name: "القمة",
    slug: "summit"
  }) {
    success
    message
    data
  }
}
```

#### إنشاء مقال
```graphql
mutation {
  createArticle(articleData: {
    title: "قمة دولية في الرياض",
    slug: "international-peace-summit-riyadh",
    excerpt: "انطلقت اليوم القمة الدولية للسلام...",
    content: "محتوى المقال الكامل...",
    featuredImage: "https://images.unsplash.com/photo-1588681664899-f142ff2dc9b1?w=800&h=500&fit=crop",
    authorId: 1,
    categoryId: 1,
    tagIds: [1, 2],
    isBreaking: true,
    isFeatured: true,
    views: 0,
    likes: 0,
    comments: 0,
    readingTime: 4,
    publishedAt: "2026-01-09T20:21:00Z"
  }) {
    success
    message
    data
  }
}
```

#### نشر مقال
```graphql
mutation {
  publishArticle(articleId: 1) {
    success
    message
    data
  }
}
```

#### تحديث مقال
```graphql
mutation {
  updateArticle(
    articleId: 1,
    title: "عنوان جديد",
    content: "محتوى محدث",
    isBreaking: true
  ) {
    success
    message
    data
  }
}
```

#### حذف مقال
```graphql
mutation {
  deleteArticle(articleId: 1) {
    success
    message
    data
  }
}
```

#### زيادة المشاهدات
```graphql
mutation {
  incrementViews(articleId: 1) {
    success
    message
    data
  }
}
```

#### زيادة الإعجابات
```graphql
mutation {
  incrementLikes(articleId: 1) {
    success
    message
    data
  }
}
```

#### إدخال بيانات تجريبية
```graphql
mutation {
  bulkInsertData {
    success
    message
    data
  }
}
```

## 📋 أمثلة على الاستخدام مع Next.js

### 1. جلب جميع المقالات
```typescript
// pages/index.tsx
import { useEffect, useState } from 'react';

export default function Home() {
  const [articles, setArticles] = useState([]);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/news/')
      .then(res => res.json())
      .then(data => setArticles(data.articles));
  }, []);
  
  return (
    <div>
      {articles.map(article => (
        <div key={article.id}>
          <h2>{article.title}</h2>
          <p>{article.excerpt}</p>
        </div>
      ))}
    </div>
  );
}
```

### 2. جلب مقال محدد
```typescript
// pages/news/[slug].tsx
import { useRouter } from 'next/router';

export default function ArticleDetail() {
  const router = useRouter();
  const { slug } = router.query;
  const [article, setArticle] = useState(null);
  
  useEffect(() => {
    if (slug) {
      fetch(`http://localhost:8000/api/news/${slug}/`)
        .then(res => res.json())
        .then(data => setArticle(data.article));
    }
  }, [slug]);
  
  return article ? (
    <div>
      <h1>{article.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: article.content }} />
    </div>
  ) : <div>Loading...</div>;
}
```

### 3. استخدام GraphQL
```typescript
// lib/graphql.ts
export async function getArticles() {
  const query = `
    query {
      allArticles {
        id
        title
        slug
        excerpt
        featuredImage
        author {
          name
          avatar
        }
        category {
          name
          color
        }
      }
    }
  `;
  
  const res = await fetch('http://localhost:8000/graphql/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query })
  });
  
  const { data } = await res.json();
  return data.allArticles;
}
```

### 4. زيادة المشاهدات
```typescript
// pages/news/[slug].tsx
const incrementViews = async (articleId: number) => {
  await fetch('http://localhost:8000/api/views/increment/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ article_id: articleId })
  });
};
```

## 🚀 تشغيل المشروع

### 1. التثبيت
```bash
# تثبيت المتطلبات
pip install -r requirements.txt

# إنشاء الملفات migrations
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# إنشاء مستخدم أدمين
python manage.py createsuperuser
```

### 2. تشغيل السيرفر
```bash
# تشغيل سيرفر Django
python manage.py runserver 8000
```

### 3. إدخال بيانات تجريبية
```bash
# عبر GraphQL
mutation {
  bulkInsertData {
    success
    message
  }
}

# أو عبر REST API
POST /api/bulk-insert/
```

### 4. الوصول إلى GraphQL Playground
```
http://localhost:8000/graphql/
```

### 5. الوصول إلى Admin Panel
```
http://localhost:8000/admin/
```

## 📁 هيكل المشروع

```
news_ddd/
├── manage.py
├── db.sqlite3
├── news_ddd/
│   ├── settings.py
│   ├── urls.py
│   ├── schema.py (GraphQL root)
│   └── ...
├── accounts/
│   ├── models.py (User)
│   └── ...
├── news/
│   ├── models.py (Article, Category, Tag, Author, Event)
│   ├── views.py (REST API)
│   ├── admin.py
│   ├── graphql/
│   │   └── schema.py (GraphQL types & mutations)
│   └── ...
├── media/
│   ├── models.py (MediaFile, ImageGallery)
│   ├── schema.py (GraphQL)
│   └── ...
└── README.md
```

## 🔐 ملاحظات أمنية

1. **في الإنتاج**: غيّر `SECRET_KEY` في `settings.py`
2. **في الإنتاج**: اضبط `DEBUG = False`
3. **في الإنتاج**: أضف `ALLOWED_HOSTS` محدد
4. **في الإنتاج**: استخدم PostgreSQL بدلاً من SQLite
5. **في الإنتاج**: أضف CORS headers للـ API

## 🎯 مميزات Event Sourcing

جميع الأحداث التالية يتم تسجيلها تلقائياً:
- `article_created` - إنشاء مقال
- `article_updated` - تحديث مقال
- `article_published` - نشر مقال
- `article_deleted` - حذف مقال
- `author_created` - إنشاء مؤلف
- `category_created` - إنشاء تصنيف
- `tag_created` - إنشاء وسم

يمكن استرجاع هذه الأحداث عبر:
```graphql
query {
  articleEvents(articleId: 1) {
    eventType
    data
    timestamp
  }
}
```

## 📞 الدعم

لأي استفسارات أو مساعدة، يرجى التواصل مع المطور.

---
**Built with Django, GraphQL, and ❤️**