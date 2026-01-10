# API Documentation - News Website

هذا المستند يشرح جميع الـ API endpoints المتاحة في النظام.

## Base URL
```
http://localhost:8000
```

## REST API Endpoints

### 1. المقالات والأخبار

#### GET /api/news/
**الوصف**: جلب جميع المقالات مع دعم الفلترة

**Parameters** (Query String):
- `category` (اختياري): فلترة حسب التصنيف (slug)
- `tag` (اختياري): فلترة حسب الوسم (slug)
- `author` (اختياري): فلترة حسب المؤلف (ID)
- `q` (اختياري): نص للبحث في العنوان والملخص والمحتوى
- `is_breaking` (اختياري): true لأخبار عاجلة فقط
- `is_featured` (اختياري): true لمقالات مميزة فقط

**Response**:
```json
{
  "articles": [
    {
      "id": 1,
      "title": "قمة دولية في الرياض",
      "slug": "international-peace-summit-riyadh",
      "excerpt": "انطلقت اليوم القمة الدولية...",
      "featured_image": "https://...",
      "author": {
        "id": 1,
        "name": "أحمد محمد",
        "avatar": "https://..."
      },
      "category": {
        "id": 1,
        "name": "السياسة",
        "slug": "politics",
        "color": "#3B82F6"
      },
      "tags": [
        {"id": 1, "name": "القمة", "slug": "summit"}
      ],
      "is_breaking": true,
      "is_featured": true,
      "views": 15420,
      "likes": 1250,
      "reading_time": 4,
      "published_at": "2026-01-09T20:21:00+03:00"
    }
  ],
  "count": 1
}
```

**Examples**:
```bash
# جميع المقالات
GET /api/news/

# مقالات في تصنيف Politics
GET /api/news/?category=politics

# أخبار عاجلة فقط
GET /api/news/?is_breaking=true

# بحث عن "سلام"
GET /api/news/?q=سلام

# مقالات مؤلف معين
GET /api/news/?author=1

# مقالات في تصنيف Politics وتحتوي على وسم summit
GET /api/news/?category=politics&tag=summit
```

---

#### POST /api/news/create/
**الوصف**: إنشاء مقال جديد

**Body** (JSON):
```json
{
  "title": "عنوان المقال",
  "slug": "slug-unique",
  "excerpt": "ملخص المقال",
  "content": "محتوى المقال الكامل",
  "featured_image": "https://image-url.com",
  "author_id": 1,
  "category_id": 1,
  "tag_ids": [1, 2],
  "is_breaking": false,
  "is_featured": false,
  "views": 0,
  "likes": 0,
  "comments": 0,
  "reading_time": 5,
  "published_at": "2026-01-09T20:21:00Z"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Article created successfully",
  "article_id": 1,
  "article_slug": "slug-unique"
}
```

---

#### GET /api/news/<id>/
**الوصف**: جلب مقال محدد مع تفاصيل كاملة

**Response**:
```json
{
  "article": {
    "id": 1,
    "title": "عنوان المقال",
    "slug": "slug-unique",
    "excerpt": "ملخص المقال",
    "content": "محتوى المقال الكامل",
    "featured_image": "https://...",
    "author": {
      "id": 1,
      "name": "أحمد محمد",
      "avatar": "https://...",
      "bio": "السيرة الذاتية",
      "role": "reporter"
    },
    "category": {
      "id": 1,
      "name": "السياسة",
      "slug": "politics",
      "color": "#3B82F6",
      "icon": "landmark"
    },
    "tags": [
      {"id": 1, "name": "القمة", "slug": "summit"}
    ],
    "is_breaking": true,
    "is_featured": true,
    "views": 15421,
    "likes": 1250,
    "comments": 340,
    "reading_time": 4,
    "published_at": "2026-01-09T20:21:00+03:00",
    "created_at": "2026-01-09T20:21:00+03:00",
    "updated_at": "2026-01-09T20:21:00+03:00",
    "related_articles": [
      {
        "id": 2,
        "title": "مقال مرتبط",
        "slug": "related-article",
        "excerpt": "ملخص مقال مرتبط",
        "featured_image": "https://..."
      }
    ]
  }
}
```

---

#### PUT /api/news/<id>/
**الوصف**: تحديث مقال موجود

**Body** (JSON):
```json
{
  "title": "عنوان محدث",
  "content": "محتوى محدث",
  "is_breaking": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "Article updated"
}
```

---

#### DELETE /api/news/<id>/
**الوصف**: حذف مقال

**Response**:
```json
{
  "success": true,
  "message": "Article deleted"
}
```

---

### 2. قوائم خاصة

#### GET /api/breaking/
**الوصف**: جلب الأخبار العاجلة (آخر 10)

**Response**:
```json
{
  "breaking_news": [
    {
      "id": 1,
      "title": "خبر عاجل",
      "slug": "breaking-news",
      "excerpt": "ملخص الخبر العاجل",
      "featured_image": "https://...",
      "published_at": "2026-01-09T20:21:00+03:00"
    }
  ],
  "count": 1
}
```

---

#### GET /api/featured/
**الوصف**: جلب المقالات المميزة (آخر 10)

**Response**:
```json
{
  "featured_articles": [
    {
      "id": 1,
      "title": "مقال مميز",
      "slug": "featured-article",
      "excerpt": "ملخص مقال مميز",
      "featured_image": "https://...",
      "published_at": "2026-01-09T20:21:00+03:00"
    }
  ],
  "count": 1
}
```

---

### 3. البيانات المرتبطة

#### GET /api/categories/
**الوصف**: جلب جميع التصنيفات

**Response**:
```json
{
  "categories": [
    {
      "id": 1,
      "name": "السياسة",
      "slug": "politics",
      "color": "#3B82F6",
      "icon": "landmark",
      "article_count": 5
    }
  ],
  "count": 1
}
```

---

#### GET /api/tags/
**الوصف**: جلب جميع الوسوم

**Response**:
```json
{
  "tags": [
    {
      "id": 1,
      "name": "القمة",
      "slug": "summit",
      "article_count": 3
    }
  ],
  "count": 1
}
```

---

#### GET /api/authors/
**الوصف**: جلب جميع المؤلفين

**Response**:
```json
{
  "authors": [
    {
      "id": 1,
      "name": "أحمد محمد",
      "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
      "bio": "مراسل سياسي متخصص في الشؤون الدولية",
      "role": "reporter",
      "article_count": 5
    }
  ],
  "count": 1
}
```

---

### 4. الإحصائيات

#### GET /api/stats/
**الوصف**: جلب إحصائيات النظام

**Response**:
```json
{
  "stats": {
    "total_articles": 6,
    "total_authors": 4,
    "total_categories": 5,
    "total_tags": 11,
    "breaking_news": 2,
    "featured_articles": 2,
    "total_views": 66310,
    "total_likes": 4780,
    "top_articles": [
      {
        "id": 6,
        "title": "انهيار في سوق الأسهم",
        "views": 18900,
        "slug": "stock-market-crash"
      }
    ],
    "articles_by_category": [
      {
        "name": "السياسة",
        "slug": "politics",
        "article_count": 1
      }
    ],
    "recent_events": [
      {
        "event_type": "article_created",
        "data": {"article_id": 1, "title": "..."},
        "timestamp": "2026-01-09T20:21:00+03:00"
      }
    ]
  }
}
```

---

### 5. الإجراءات

#### POST /api/views/increment/
**الوصف**: زيادة عدد مشاهدات مقال

**Body**:
```json
{
  "article_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "article_id": 1,
  "views": 15421
}
```

---

#### POST /api/likes/increment/
**الوصف**: زيادة عدد إعجابات مقال

**Body**:
```json
{
  "article_id": 1
}
```

**Response**:
```json
{
  "success": true,
  "article_id": 1,
  "likes": 1251
}
```

---

#### POST /api/bulk-insert/
**الوصف**: إدخال بيانات تجريبية (للتطوير فقط)

**Response**:
```json
{
  "success": true,
  "message": "Data inserted successfully! Created: 4 authors, 5 categories, 11 tags, 6 articles",
  "data": {
    "authors": 4,
    "categories": 5,
    "tags": 11,
    "articles": 6
  }
}
```

---

#### GET /api/health/
**الوصف**: فحص صحة النظام

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-09T20:21:00+03:00",
  "service": "news-api",
  "version": "1.0.0"
}
```

---

## GraphQL API

### Endpoint
```
POST /graphql/
Content-Type: application/json
```

### Query Types

#### 1. allArticles
جلب جميع المقالات
```graphql
query {
  allArticles {
    id
    title
    slug
    excerpt
    content
    featuredImage
    author {
      id
      name
      avatar
      bio
      role
    }
    category {
      id
      name
      slug
      color
      icon
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
    comments
    readingTime
    publishedAt
    createdAt
    updatedAt
  }
}
```

#### 2. articleById
جلب مقال محدد
```graphql
query {
  articleById(articleId: 1) {
    id
    title
    content
    author {
      name
      avatar
    }
    views
    likes
  }
}
```

#### 3. articleBySlug
جلب مقال حسب Slug
```graphql
query {
  articleBySlug(slug: "international-peace-summit-riyadh") {
    id
    title
    content
    author {
      name
    }
  }
}
```

#### 4. breakingArticles
أخبار عاجلة
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

#### 5. featuredArticles
مقالات مميزة
```graphql
query {
  featuredArticles {
    id
    title
    excerpt
    featuredImage
  }
}
```

#### 6. publishedArticles
أخبار منشورة فقط
```graphql
query {
  publishedArticles {
    id
    title
    publishedAt
  }
}
```

#### 7. searchArticles
بحث في المقالات
```graphql
query {
  searchArticles(query: "سلام") {
    id
    title
    excerpt
  }
}
```

#### 8. articlesByAuthor
مقالات حسب المؤلف
```graphql
query {
  articlesByAuthor(authorId: 1) {
    id
    title
    excerpt
  }
}
```

#### 9. articlesByCategory
مقالات حسب التصنيف
```graphql
query {
  articlesByCategory(categorySlug: "politics") {
    id
    title
    excerpt
  }
}
```

#### 10. allCategories
جميع التصنيفات
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

#### 11. allTags
جميع الوسوم
```graphql
query {
  allTags {
    id
    name
    slug
  }
}
```

#### 12. allAuthors
جميع المؤلفين
```graphql
query {
  allAuthors {
    id
    name
    avatar
    bio
    role
  }
}
```

#### 13. articleEvents
أحداث مقال معين
```graphql
query {
  articleEvents(articleId: 1) {
    eventType
    data
    timestamp
  }
}
```

#### 14. publishedEvents
جميع الأحداث المنشورة
```graphql
query {
  publishedEvents {
    eventType
    data
    timestamp
  }
}
```

### Mutation Types

#### 1. createAuthor
إنشاء مؤلف
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

#### 2. createCategory
إنشاء تصنيف
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

#### 3. createTag
إنشاء وسم
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

#### 4. createArticle
إنشاء مقال
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

#### 5. publishArticle
نشر مقال
```graphql
mutation {
  publishArticle(articleId: 1) {
    success
    message
    data
  }
}
```

#### 6. updateArticle
تحديث مقال
```graphql
mutation {
  updateArticle(
    articleId: 1,
    title: "عنوان محدث",
    content: "محتوى محدث",
    isBreaking: true
  ) {
    success
    message
    data
  }
}
```

#### 7. deleteArticle
حذف مقال
```graphql
mutation {
  deleteArticle(articleId: 1) {
    success
    message
    data
  }
}
```

#### 8. incrementViews
زيادة المشاهدات
```graphql
mutation {
  incrementViews(articleId: 1) {
    success
    message
    data
  }
}
```

#### 9. incrementLikes
زيادة الإعجابات
```graphql
mutation {
  incrementLikes(articleId: 1) {
    success
    message
    data
  }
}
```

#### 10. bulkInsertData
إدخال بيانات تجريبية
```graphql
mutation {
  bulkInsertData {
    success
    message
    data
  }
}
```

---

## أخطاء شائعة

### 404 Not Found
```json
{
  "error": "Article not found"
}
```

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 500 Internal Server Error
```json
{
  "error": "Detailed error message"
}
```

---

## ملاحظات

1. جميع الـ API endpoints تدعم CORS للتكامل مع Next.js
2. GraphQL playground متاح على `/graphql/`
3. Admin panel متاح على `/admin/`
4. جميع الأحداث يتم تسجيلها في Event model
5. المشاهدات تزيد تلقائياً عند جلب مقال محدد
6. البيانات التجريبية يمكن إدخالها عبر `/api/bulk-insert/` أو GraphQL mutation