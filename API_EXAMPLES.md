# API Examples - Next.js Integration

أمثلة عملية لاستخدام الـ API مع Next.js

## 1. إعدادات أساسية (lib/api.ts)

```typescript
// lib/api.ts
const API_BASE_URL = 'http://localhost:8000';

export const api = {
  // REST API
  rest: {
    async getArticles(filters?: Record<string, any>) {
      const params = new URLSearchParams(filters || {});
      const url = `${API_BASE_URL}/api/news/?${params}`;
      const res = await fetch(url);
      return res.json();
    },

    async getArticleById(id: number) {
      const res = await fetch(`${API_BASE_URL}/api/news/${id}/`);
      return res.json();
    },

    async getArticleBySlug(slug: string) {
      const res = await fetch(`${API_BASE_URL}/api/news/?slug=${slug}`);
      const data = await res.json();
      return data.articles[0];
    },

    async getBreakingNews() {
      const res = await fetch(`${API_BASE_URL}/api/breaking/`);
      return res.json();
    },

    async getFeaturedArticles() {
      const res = await fetch(`${API_BASE_URL}/api/featured/`);
      return res.json();
    },

    async getCategories() {
      const res = await fetch(`${API_BASE_URL}/api/categories/`);
      return res.json();
    },

    async getTags() {
      const res = await fetch(`${API_BASE_URL}/api/tags/`);
      return res.json();
    },

    async getAuthors() {
      const res = await fetch(`${API_BASE_URL}/api/authors/`);
      return res.json();
    },

    async getStats() {
      const res = await fetch(`${API_BASE_URL}/api/stats/`);
      return res.json();
    },

    async incrementViews(articleId: number) {
      const res = await fetch(`${API_BASE_URL}/api/views/increment/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ article_id: articleId })
      });
      return res.json();
    },

    async incrementLikes(articleId: number) {
      const res = await fetch(`${API_BASE_URL}/api/likes/increment/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ article_id: articleId })
      });
      return res.json();
    },

    async createArticle(articleData: any) {
      const res = await fetch(`${API_BASE_URL}/api/news/create/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(articleData)
      });
      return res.json();
    }
  },

  // GraphQL API
  graphql: async (query: string, variables?: any) => {
    const res = await fetch(`${API_BASE_URL}/graphql/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, variables })
    });
    const { data, errors } = await res.json();
    if (errors) throw new Error(errors[0].message);
    return data;
  }
};
```

## 2. صفحة الرئيسية - عرض المقالات (pages/index.tsx)

```typescript
// pages/index.tsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function Home() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    try {
      const data = await api.rest.getArticles();
      setArticles(data.articles);
    } catch (error) {
      console.error('Error loading articles:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="container">
      <h1>Latest News</h1>
      <div className="articles-grid">
        {articles.map((article: any) => (
          <article key={article.id} className="article-card">
            {article.featured_image && (
              <img src={article.featured_image} alt={article.title} />
            )}
            <div className="content">
              <span className="category" style={{ color: article.category?.color }}>
                {article.category?.name}
              </span>
              <h2>{article.title}</h2>
              <p>{article.excerpt}</p>
              <div className="meta">
                <span>👁️ {article.views}</span>
                <span>❤️ {article.likes}</span>
                <span>⏱️ {article.reading_time} min</span>
              </div>
              {article.is_breaking && (
                <span className="breaking-badge">عاجل</span>
              )}
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
```

## 3. صفحة تفاصيل المقال (pages/news/[slug].tsx)

```typescript
// pages/news/[slug].tsx
import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { api } from '@/lib/api';

export default function ArticleDetail() {
  const router = useRouter();
  const { slug } = router.query;
  const [article, setArticle] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) {
      loadArticle();
    }
  }, [slug]);

  const loadArticle = async () => {
    try {
      // Using REST API
      const data = await api.rest.getArticleBySlug(slug as string);
      setArticle(data);

      // Increment views
      if (data?.id) {
        await api.rest.incrementViews(data.id);
      }
    } catch (error) {
      console.error('Error loading article:', error);
      router.push('/404');
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async () => {
    if (article?.id) {
      const result = await api.rest.incrementLikes(article.id);
      setArticle((prev: any) => ({ ...prev, likes: result.likes }));
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!article) return <div>Article not found</div>;

  return (
    <div className="article-detail">
      {article.featured_image && (
        <img 
          src={article.featured_image} 
          alt={article.title}
          className="featured-image"
        />
      )}
      
      <div className="article-header">
        <span className="category" style={{ background: article.category?.color }}>
          {article.category?.name}
        </span>
        <h1>{article.title}</h1>
        <div className="author-info">
          <img src={article.author?.avatar} alt={article.author?.name} />
          <div>
            <strong>{article.author?.name}</strong>
            <p>{article.author?.bio}</p>
          </div>
        </div>
      </div>

      <div 
        className="article-content"
        dangerouslySetInnerHTML={{ __html: article.content }}
      />

      <div className="article-tags">
        {article.tags?.map((tag: any) => (
          <span key={tag.id} className="tag">
            #{tag.name}
          </span>
        ))}
      </div>

      <div className="article-actions">
        <button onClick={handleLike}>
          ❤️ {article.likes} إعجاب
        </button>
        <span>👁️ {article.views} مشاهدة</span>
        <span>⏱️ {article.reading_time} دقيقة</span>
      </div>

      {article.related_articles?.length > 0 && (
        <div className="related-articles">
          <h3>مقالات ذات صلة</h3>
          <div className="related-grid">
            {article.related_articles.map((related: any) => (
              <div key={related.id} className="related-card">
                {related.featured_image && (
                  <img src={related.featured_image} alt={related.title} />
                )}
                <h4>{related.title}</h4>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

## 4. صفحة الأخبار العاجلة (pages/breaking.tsx)

```typescript
// pages/breaking.tsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function BreakingNews() {
  const [breaking, setBreaking] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBreakingNews();
  }, []);

  const loadBreakingNews = async () => {
    try {
      const data = await api.rest.getBreakingNews();
      setBreaking(data.breaking_news);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="breaking-page">
      <h1>🚨 الأخبار العاجلة</h1>
      <div className="breaking-list">
        {breaking.map((news: any) => (
          <div key={news.id} className="breaking-item">
            <span className="badge">عاجل</span>
            <h2>{news.title}</h2>
            <p>{news.excerpt}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 5. صفحة البحث (pages/search.tsx)

```typescript
// pages/search.tsx
import { useState } from 'react';
import { api } from '@/lib/api';
import { useRouter } from 'next/router';

export default function Search() {
  const router = useRouter();
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (query: string) => {
    if (!query) return;
    
    setLoading(true);
    try {
      // Using GraphQL
      const data = await api.graphql(`
        query($query: String!) {
          searchArticles(query: $query) {
            id
            title
            excerpt
            featuredImage
            category {
              name
              color
            }
            author {
              name
            }
          }
        }
      `, { query });
      
      setResults(data.searchArticles);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="search-page">
      <input
        type="text"
        placeholder="ابحث عن الأخبار..."
        onChange={(e) => handleSearch(e.target.value)}
      />
      
      {loading && <div>جاري البحث...</div>}
      
      <div className="results">
        {results.map((article: any) => (
          <div key={article.id} className="result-item">
            <h3>{article.title}</h3>
            <p>{article.excerpt}</p>
            <span style={{ color: article.category?.color }}>
              {article.category?.name}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 6. استخدام GraphQL بدلاً من REST (pages/graphql-demo.tsx)

```typescript
// pages/graphql-demo.tsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function GraphQLDemo() {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const data = await api.graphql(`
        query {
          allArticles {
            id
            title
            excerpt
            author {
              name
              avatar
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
          allCategories {
            id
            name
            slug
            color
          }
        }
      `);
      
      setArticles(data.allArticles);
      setCategories(data.allCategories);
    } catch (error) {
      console.error('GraphQL error:', error);
    }
  };

  return (
    <div>
      <h1>GraphQL Demo</h1>
      
      <h2>Categories</h2>
      <ul>
        {categories.map((cat: any) => (
          <li key={cat.id} style={{ color: cat.color }}>
            {cat.name} ({cat.slug})
          </li>
        ))}
      </ul>

      <h2>Articles</h2>
      {articles.map((article: any) => (
        <div key={article.id} style={{ marginBottom: '20px' }}>
          <h3>{article.title}</h3>
          <p>{article.excerpt}</p>
          <small>
            By: {article.author.name} | 
            Category: {article.category.name} | 
            Views: {article.views} | 
            Likes: {article.likes}
          </small>
        </div>
      ))}
    </div>
  );
}
```

## 7. Admin Dashboard (pages/admin.tsx)

```typescript
// pages/admin.tsx
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const data = await api.rest.getStats();
      setStats(data.stats);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const insertMockData = async () => {
    if (confirm('هل تريد إدخال بيانات تجريبية؟')) {
      const result = await api.rest.bulkInsertData();
      alert(result.message);
      loadStats();
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="admin-dashboard">
      <h1>لوحة التحكم</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>المقالات</h3>
          <p>{stats?.total_articles}</p>
        </div>
        <div className="stat-card">
          <h3>المؤلفين</h3>
          <p>{stats?.total_authors}</p>
        </div>
        <div className="stat-card">
          <h3>التصنيفات</h3>
          <p>{stats?.total_categories}</p>
        </div>
        <div className="stat-card">
          <h3>الوسوم</h3>
          <p>{stats?.total_tags}</p>
        </div>
        <div className="stat-card">
          <h3>عاجل</h3>
          <p>{stats?.breaking_news}</p>
        </div>
        <div className="stat-card">
          <h3>مميز</h3>
          <p>{stats?.featured_articles}</p>
        </div>
      </div>

      <div className="actions">
        <button onClick={insertMockData}>إدخال بيانات تجريبية</button>
      </div>

      <h2>أعلى المقالات مشاهدة</h2>
      <ul>
        {stats?.top_articles?.map((article: any) => (
          <li key={article.id}>
            {article.title} - {article.views} مشاهدة
          </li>
        ))}
      </ul>

      <h2>المقالات حسب التصنيف</h2>
      <ul>
        {stats?.articles_by_category?.map((cat: any) => (
          <li key={cat.slug}>
            {cat.name}: {cat.article_count} مقال
          </li>
        ))}
      </ul>
    </div>
  );
}
```

## 8. مكون مشترك - Article Card (components/ArticleCard.tsx)

```typescript
// components/ArticleCard.tsx
import { api } from '@/lib/api';

interface ArticleCardProps {
  article: any;
  variant?: 'default' | 'featured' | 'compact';
}

export default function ArticleCard({ article, variant = 'default' }: ArticleCardProps) {
  const handleView = async () => {
    await api.rest.incrementViews(article.id);
  };

  const handleLike = async (e: React.MouseEvent) => {
    e.stopPropagation();
    const result = await api.rest.incrementLikes(article.id);
    article.likes = result.likes;
  };

  if (variant === 'compact') {
    return (
      <div className="article-compact" onClick={handleView}>
        <h4>{article.title}</h4>
        <small>{article.category?.name} • {article.views} views</small>
      </div>
    );
  }

  if (variant === 'featured') {
    return (
      <div className="article-featured" onClick={handleView}>
        {article.featured_image && (
          <img src={article.featured_image} alt={article.title} />
        )}
        <div className="content">
          <span className="badge" style={{ background: article.category?.color }}>
            {article.category?.name}
          </span>
          <h2>{article.title}</h2>
          <p>{article.excerpt}</p>
          <div className="meta">
            <span onClick={handleLike}>❤️ {article.likes}</span>
            <span>👁️ {article.views}</span>
            <span>⏱️ {article.reading_time} min</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="article-card" onClick={handleView}>
      {article.featured_image && (
        <img src={article.featured_image} alt={article.title} />
      )}
      <div className="content">
        <span className="category" style={{ color: article.category?.color }}>
          {article.category?.name}
        </span>
        <h3>{article.title}</h3>
        <p>{article.excerpt}</p>
        <div className="meta">
          <span onClick={handleLike}>❤️ {article.likes}</span>
          <span>👁️ {article.views}</span>
        </div>
        {article.is_breaking && <span className="breaking">عاجل</span>}
        {article.is_featured && <span className="featured">مميز</span>}
      </div>
    </div>
  );
}
```

## 9. Hook مخصص للبيانات (hooks/useNews.ts)

```typescript
// hooks/useNews.ts
import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export function useNews(filters = {}) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, [JSON.stringify(filters)]);

  const loadData = async () => {
    try {
      setLoading(true);
      const result = await api.rest.getArticles(filters);
      setData(result.articles);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return { data, loading, error, refetch: loadData };
}

export function useArticle(slug: string) {
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (slug) loadArticle();
  }, [slug]);

  const loadArticle = async () => {
    try {
      setLoading(true);
      const result = await api.rest.getArticleBySlug(slug);
      setArticle(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const incrementViews = async () => {
    if (article?.id) {
      await api.rest.incrementViews(article.id);
    }
  };

  const incrementLikes = async () => {
    if (article?.id) {
      const result = await api.rest.incrementLikes(article.id);
      setArticle((prev: any) => ({ ...prev, likes: result.likes }));
    }
  };

  return { article, loading, error, incrementViews, incrementLikes, refetch: loadArticle };
}

export function useCategories() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCategories();
  }, []);

  const loadCategories = async () => {
    try {
      const result = await api.rest.getCategories();
      setCategories(result.categories);
    } finally {
      setLoading(false);
    }
  };

  return { categories, loading };
}
```

## 10. Next.js API Route للتعامل مع الـ API (pages/api/proxy/[...path].ts)

```typescript
// pages/api/proxy/[...path].ts
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { path } = req.query;
  const API_URL = 'http://localhost:8000';
  
  // Construct the full URL
  const targetUrl = `${API_URL}/api/${Array.isArray(path) ? path.join('/') : path}`;
  
  try {
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...(req.headers.cookie && { Cookie: req.headers.cookie })
      },
      body: req.body ? JSON.stringify(req.body) : undefined
    });

    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Proxy error' });
  }
}
```

## ملاحظات استخدام

### مع Next.js App Router (Next.js 13+)

```typescript
// app/page.tsx
import { api } from '@/lib/api';

export default async function Home() {
  const data = await api.rest.getArticles();
  
  return (
    <div>
      {data.articles.map((article: any) => (
        <div key={article.id}>
          <h2>{article.title}</h2>
        </div>
      ))}
    </div>
  );
}
```

### مع TypeScript

```typescript
// types/article.ts
export interface Article {
  id: number;
  title: string;
  slug: string;
  excerpt: string;
  content: string;
  featured_image?: string;
  author: {
    id: number;
    name: string;
    avatar: string;
    bio: string;
    role: string;
  };
  category: {
    id: number;
    name: string;
    slug: string;
    color: string;
    icon: string;
  };
  tags: Array<{
    id: number;
    name: string;
    slug: string;
  }>;
  is_breaking: boolean;
  is_featured: boolean;
  views: number;
  likes: number;
  comments: number;
  reading_time: number;
  published_at: string;
  created_at: string;
  updated_at: string;
}
```

### مع SWR (Data Fetching Library)

```typescript
// hooks/useArticles.ts
import useSWR from 'swr';
import { api } from '@/lib/api';

export function useArticles(filters?: any) {
  const { data, error, isLoading, mutate } = useSWR(
    `articles-${JSON.stringify(filters)}`,
    () => api.rest.getArticles(filters)
  );

  return {
    articles: data?.articles,
    isLoading,
    error,
    mutate
  };
}
```

### مع React Query

```typescript
// hooks/useArticles.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api';

export function useArticles(filters?: any) {
  return useQuery({
    queryKey: ['articles', filters],
    queryFn: () => api.rest.getArticles(filters)
  });
}

export function useIncrementViews() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (articleId: number) => api.rest.incrementViews(articleId),
    onSuccess: () => {
      queryClient.invalidateQueries(['articles']);
    }
  });
}
```

هذه الأمثلة تغطي:
- ✅ جلب المقالات
- ✅ عرض تفاصيل المقال
- ✅ البحث
- ✅ زيادة المشاهدات والإعجابات
- ✅ استخدام GraphQL
- ✅ إنشاء مقالات جديدة
- ✅ لوحة التحكم
- ✅ مكونات قابلة لإعادة الاستخدام
- ✅ Hooks مخصصة
- ✅ TypeScript
- ✅ Next.js App Router