# News DDD — News Backend API

Django backend for an Arabic-language news site, built to be consumed by a
Next.js frontend. REST (primary) and GraphQL (compatibility, pending
confirmation of frontend usage — see "GraphQL" below).

## Architecture

```
accounts/            User (role: admin/editor/reporter/reader) + Author
                      permissions.py — shared role checks (REST + GraphQL)

news/
  models.py           Category, Tag, Article (status workflow), ArticleLike, AuditLog
  selectors.py         read-side queries (published articles, search, related, ...)
  services.py           write-side domain rules (publish/archive/submit/like/view-count)
  api/                  REST API — serializers, permissions, viewsets, filters, /api/v1/
  graphql/schema.py      GraphQL schema (secured, matches current models)
  views.py               legacy read-only endpoints kept for compatibility
  management/commands/seed_news.py   local dev seed data (no HTTP endpoint, no hardcoded password)

news_ddd/             settings, root urls, wsgi/asgi
```

Not microservices, not event sourcing, not CQRS as a framework — just Django
apps split by responsibility (read queries vs. write rules vs. HTTP layer).

## Article publication workflow

`Article.status`: `draft` → `pending_review` → `published` → `archived`.
Transitions are enforced in `news/services.py`, not by directly PATCHing the
`status` field — e.g. a reporter can submit for review, only an editor/admin
can publish, and an archived article can't be re-published without going
back through draft.

## REST API (`/api/v1/`)

* `GET /api/v1/articles/` — published articles only for anonymous/reader
  callers; filters: `category`, `tag`, `author`, `is_breaking`, `is_featured`,
  `published_after`, `published_before`; `search=`; `ordering=`; paginated.
* `GET /api/v1/articles/<slug>/` — detail (increments view count atomically).
* `POST /api/v1/articles/` — create (reporter role or above; JWT/session auth
  required). `views`/`likes`/`comments`/`status` are never client-writable.
* `POST /api/v1/articles/<slug>/submit_for_review/` / `publish/` / `archive/`
  / `like/` — lifecycle actions, each permission-checked.
* `GET/POST /api/v1/categories/`, `/api/v1/tags/` — write access is admin-only.
* `GET /api/v1/authors/` — read-only, never exposes email/phone.
* `GET /api/v1/breaking/`, `/api/v1/featured/`, `/api/v1/health/`.
* `POST /api/v1/auth/token/`, `/api/v1/auth/token/refresh/` — JWT.

Every response is `{"success": true, "data": ...}` or
`{"success": false, "error": {"code": ..., "message": ...}}` — no raw
tracebacks or database errors ever reach the client.

## Legacy endpoints

`/api/news/`, `/api/breaking/`, `/api/featured/`, `/api/categories/`,
`/api/tags/`, `/api/authors/`, `/api/health/` still work, **read-only**, for
an existing frontend integration. The old unauthenticated write endpoints
(create/update/delete article, increment views/likes, bulk-insert mock data,
and the public user list that exposed emails) have been removed — use
`/api/v1/` for writes.

## GraphQL

Kept at `/graphql/`, with the same role checks as REST and the mock-data
`bulkInsertData` mutation removed, **pending confirmation that the frontend
actually uses it**. If it isn't in use, the recommendation is to remove it
and consolidate on `/api/v1/` to avoid maintaining two APIs.

## Roles

`admin` (full access, or `is_superuser`), `editor` (review/publish/archive
any article), `reporter` (create/edit own articles, submit for review),
`reader` (read only). Defined once in `accounts/permissions.py`.

## Local development

```bash
cp .env.example .env    # fill in SECRET_KEY (see below), leave DEBUG=True
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_news --password "SomeLocalDevPassword!23"
python manage.py runserver
```

Generate a `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Testing

```bash
python manage.py test
```

Covers: publish/archive domain rules, atomic view increments, like
idempotency, anonymous read/write permission boundaries, draft visibility,
pagination, and a regression test for the admin user change-page.

## Deployment (Render)

`build.sh` installs dependencies, runs `collectstatic`, and applies
migrations. `Procfile` runs Gunicorn. Required environment variables on
Render: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`, `DATABASE_URL`
(set automatically if you attach a Render Postgres instance),
`CORS_ALLOWED_ORIGINS` (your deployed frontend origin(s)).

`DEBUG=False` in production means `SECRET_KEY` **must** be set — the app
refuses to start otherwise rather than falling back to an insecure default.

## Database

Postgres in production (via `DATABASE_URL`), SQLite for local development
only. `db.sqlite3` is gitignored and no longer tracked in version control.
