# 100-Day E-Commerce Platform — Implementation Plan

> Goal: Build a production-ready e-commerce platform and reach middle+ Python backend engineer level by Day 100.

---

## Table of Contents

| Phase | Days | Title |
|-------|------|-------|
| [Phase 1](#phase-1-days-17--foundations--naive-crud) | 1–7 | Foundations & Naive CRUD |
| [Phase 2](#phase-2-days-815--layered-architecture--authentication) | 8–15 | Layered Architecture & Authentication |
| [Phase 3](#phase-3-days-1623--sellers-attributes-variants--inventory) | 16–23 | Sellers, Attributes, Variants & Inventory |
| [Phase 4](#phase-4-days-2430--query-performance--pagination) | 24–30 | Query Performance & Pagination |
| [Phase 5](#phase-5-days-3138--cart-checkout--transactional-integrity) | 31–38 | Cart, Checkout & Transactional Integrity |
| [Phase 6](#phase-6-days-3946--orders-payments--outbox-pattern) | 39–46 | Orders, Payments & Outbox Pattern |
| [Phase 7](#phase-7-days-4754--caching-redis--background-jobs) | 47–54 | Caching, Redis & Background Jobs |
| [Phase 8](#phase-8-days-5563--microservices-split-django-catalog--django-delivery--warehouse) | 55–63 | Microservices Split (Django Catalog + Delivery & Warehouse) |
| [Phase 9](#phase-9-days-6471--event-driven-architecture-kafka--product-activity-monitor) | 64–71 | Event-Driven Architecture, Kafka & Product Activity Monitor |
| [Phase 10](#phase-10-days-7279--search-reviews--polyglot-persistence) | 72–79 | Search, Reviews & Polyglot Persistence |
| [Phase 11](#phase-11-days-8086--cicd-multi-stage-docker--iac) | 80–86 | CI/CD, Multi-Stage Docker & IaC |
| [Phase 12](#phase-12-days-8793--kubernetes-helm--autoscaling) | 87–93 | Kubernetes, Helm & Autoscaling |
| [Phase 13](#phase-13-days-94100--observability-resilience--portfolio-readiness) | 94–100 | Observability, Resilience & Portfolio Readiness |
| [Final Service Map](#final-service-map-day-100) | — | Complete service topology |
| [ADR Index](#adr-index) | — | All Architecture Decision Records |

---

## Prerequisites — Install Before Day 1

Before starting Day 1, make sure the following are available on your machine:

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Primary backend language |
| Node.js | 20 LTS | React frontend |
| Docker Desktop | Latest | Containers |
| `docker compose` (v2) | Latest | Local orchestration |
| Git | 2.x | Version control |
| `psql` CLI | 16 | Inspect PostgreSQL directly |
| `kubectl` | 1.29+ | Needed in Phase 12 |
| `helm` | 3.x | Needed in Phase 12 |
| `kind` or `minikube` | Latest | Local Kubernetes (Phase 12) |
| Terraform | 1.7+ | IaC (Phase 11) |

> Install Python dependencies with `uv` (fast, modern) or plain `pip`. All commands in this plan use `pip` for clarity but `uv pip install` is a drop-in replacement.

---

## Phase 1: Days 1–7 — Foundations & Naive CRUD

**Phase objective:** Bootstrap the FastAPI monolith with SQLAlchemy + asyncpg, build Product/Category CRUD, scaffold React frontend, wire Docker Compose, and write the first integration tests.

---

### Project Architecture

**Architecture style:** Single-process monolith

**What changed from Phase 0 (nothing before):**
- Added: React + TypeScript frontend
- Added: FastAPI monolith service
- Added: PostgreSQL database
- Added: Docker Compose orchestration

**System diagram (end of Phase 1):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON HTTP
    ↓
[FastAPI Monolith :8000]
    | SQL (asyncpg / SQLAlchemy async)
    ↓
[PostgreSQL :5432]

[Docker Compose wraps all above]
```

**Data flow — Create Product (most complex new operation):**
1. User fills product form in React → POST /api/products (JSON body)
2. FastAPI router receives request → validates via Pydantic schema
3. SQLAlchemy async session → INSERT INTO products (name, price, sku, category_id)
4. PostgreSQL writes row, returns id
5. FastAPI serializes row → JSON response 201 Created
6. React receives response → updates product list state

---

### Business Features
- [ ] Admin can create, read, update, delete products
- [ ] Admin can create, read, update, delete categories
- [ ] Products belong to a category
- [ ] Basic product list visible in browser

---

#### Day 1 — Project scaffolding & repo setup
**Daily Time Budget: ~5h**

- [ ] Create GitHub repo, clone locally, set up `.gitignore` for Python/Node (20 min)
- [ ] Initialize Python 3.12 virtual environment, install `fastapi uvicorn sqlalchemy asyncpg alembic pydantic-settings python-dotenv structlog` (30 min)
- [ ] Create `pyproject.toml` with project metadata and tool config (black, ruff, mypy) (30 min)
- [ ] Scaffold folder structure: `app/`, `app/api/`, `app/models/`, `app/schemas/`, `app/core/`, `alembic/` (20 min)
- [ ] Write `app/core/config.py` using `pydantic-settings` — load `DATABASE_URL`, `DEBUG`, `SECRET_KEY` from `.env` (45 min)
- [ ] Write `app/core/database.py` — async SQLAlchemy engine + `AsyncSession` factory + `get_db` dependency (1h)
- [ ] Write `app/main.py` — create FastAPI app, include routers, add structlog middleware that logs `method`, `path`, `status_code`, `duration_ms` (45 min)
- [ ] Confirm `uvicorn app.main:app --reload` starts and `/docs` is accessible (15 min)

---

#### Day 2 — SQLAlchemy models & Alembic migrations
**Daily Time Budget: ~5h**

- [ ] Write `app/models/base.py` — `Base = declarative_base()`, `TimestampMixin` with `created_at`, `updated_at` columns using `server_default=func.now()` (30 min)
- [ ] Write `app/models/category.py` — `Category` model: `id`, `name`, `slug`, `description`, `parent_id` (self-referential FK) (45 min)
- [ ] Write `app/models/product.py` — `Product` model: `id`, `name`, `description`, `price` (Numeric 10,2), `sku` (unique), `category_id` (FK), `is_active`, timestamps (45 min)
- [ ] Configure `alembic.ini` and `alembic/env.py` to use async engine and import `Base.metadata` (1h)
- [ ] Run `alembic revision --autogenerate -m "create products and categories"` — inspect generated migration file (30 min)
- [ ] Run `alembic upgrade head` against local PostgreSQL — verify tables exist with `\d products` in psql (20 min)
- [ ] Write `app/schemas/product.py` — `ProductCreate`, `ProductUpdate`, `ProductRead` Pydantic models (45 min)
- [ ] Write `app/schemas/category.py` — `CategoryCreate`, `CategoryUpdate`, `CategoryRead` Pydantic models (25 min)

---

#### Day 3 — CRUD endpoints for Category and Product
**Daily Time Budget: ~5.5h**

- [ ] Write `app/api/categories.py` — `GET /categories`, `POST /categories`, `GET /categories/{id}`, `PUT /categories/{id}`, `DELETE /categories/{id}` using raw async session (1.5h)
- [ ] Write `app/api/products.py` — same five endpoints for products (1.5h)
- [ ] Register both routers in `app/main.py` under `/api/v1` prefix (15 min)
- [ ] Add `HTTPException` 404 handling when row not found; add 422 validation error handler that returns structured JSON (45 min)
- [ ] Test all endpoints manually via Swagger UI `/docs` — create 2 categories, create 3 products, update one, delete one (30 min)
- [ ] Add `response_model` to all endpoints and verify extra fields are stripped (30 min)
- [ ] Write `app/core/exceptions.py` — `NotFoundError`, `ConflictError` custom exceptions + handlers registered on the app (30 min)

---

#### Day 4 — Docker & Docker Compose
**Daily Time Budget: ~5h**

- [ ] Write `Dockerfile` for FastAPI — use `python:3.12-slim`, multi-stage NOT yet (keep simple), install deps from `requirements.txt`, expose 8000 (45 min)
- [ ] Write `docker-compose.yml` with services: `api` (FastAPI), `db` (postgres:16-alpine) with volume, health check on db (1h)
- [ ] Add `.env.example` file with all required env vars; document each in a comment (20 min)
- [ ] Confirm `docker compose up --build` starts both services and `/docs` is reachable at `localhost:8000` (30 min)
- [ ] Run Alembic migrations inside container on startup via `entrypoint.sh` — `alembic upgrade head && uvicorn ...` (45 min)
- [ ] Scaffold React app: `npm create vite@latest frontend -- --template react-ts` (20 min)
- [ ] Add `frontend` service to `docker-compose.yml` — Node 20, mount `./frontend`, expose 3000 (30 min)
- [ ] Confirm all three services start together: React at :3000, FastAPI at :8000, Postgres at :5432 (30 min)

---

#### Day 5 — React product list & category list UI
**Daily Time Budget: ~5h**

- [ ] Install Axios + React Query (`@tanstack/react-query`) in frontend (20 min)
- [ ] Create `src/api/client.ts` — Axios instance with `baseURL=http://localhost:8000/api/v1` (20 min)
- [ ] Create `src/api/products.ts` — `getProducts()`, `createProduct()`, `updateProduct()`, `deleteProduct()` functions (45 min)
- [ ] Create `src/api/categories.ts` — same pattern for categories (30 min)
- [ ] Create `src/components/ProductList.tsx` — fetch and display products in a table using `useQuery` (1h)
- [ ] Create `src/components/ProductForm.tsx` — controlled form for create/edit with `useMutation` (1h)
- [ ] Wire up `App.tsx` with basic routing (React Router v6): `/products`, `/categories` (30 min)
- [ ] Confirm product create → list refresh works end-to-end in browser (15 min)

---

#### Day 6 — Integration tests setup
**Daily Time Budget: ~5h**

- [ ] Install `pytest pytest-asyncio httpx anyio` in dev dependencies (20 min)
- [ ] Write `tests/conftest.py` — async test client using `httpx.AsyncClient`, test DB setup: create fresh schema before each test session, drop after (1.5h)
- [ ] Write `tests/test_categories.py` — test `POST /categories` (success, duplicate slug 409), `GET /categories` (empty list, populated), `GET /categories/{id}` (found, 404), `DELETE /categories/{id}` (1.5h)
- [ ] Write `tests/test_products.py` — test `POST /products` (success, missing required field 422, unknown category_id 404), `GET /products`, `PUT /products/{id}` (1h)
- [ ] Run `pytest -v` — confirm all tests pass (20 min)
- [ ] Add `pytest.ini` with `asyncio_mode = auto` (10 min)

---

#### Day 7 — Polish, CORS, structlog & CI skeleton
**Daily Time Budget: ~4.5h**

- [ ] Add CORS middleware to FastAPI app — allow `http://localhost:3000` for now (20 min)
- [ ] Verify React frontend can call FastAPI without CORS error in browser console (15 min)
- [ ] Add `X-Request-ID` middleware — generate UUID per request, attach to structlog context, return in response header (45 min)
- [ ] Configure structlog to output JSON in production (`DEBUG=false`) and colored console in dev (`DEBUG=true`) (45 min)
- [ ] Write `.github/workflows/ci.yml` — trigger on push/PR, run `ruff check`, `mypy`, `pytest` (1h)
- [ ] Fix any ruff or mypy errors found during CI run (30 min)
- [ ] Update `README.md` with setup instructions, `docker compose up` quickstart (30 min)

---

### Frontend Tasks
- [ ] Scaffold Vite + React + TypeScript project (20 min)
- [ ] Set up React Query provider in `main.tsx` (15 min)
- [ ] Build `ProductList` component with table + delete button (1h)
- [ ] Build `ProductForm` component for create and edit (1h)
- [ ] Build `CategoryList` and `CategoryForm` components (1h)
- [ ] Add React Router v6 with `/products` and `/categories` routes (30 min)

### Database Changes
- [ ] Create `categories` table: `id`, `name`, `slug` (unique), `description`, `parent_id`, timestamps (45 min)
- [ ] Create `products` table: `id`, `name`, `description`, `price`, `sku` (unique), `category_id` FK, `is_active`, timestamps (45 min)
- [ ] Alembic initial migration — verify both tables, FK constraint, unique constraints (30 min)

### DevOps & Infrastructure Tasks
- [ ] Write FastAPI `Dockerfile` (single-stage, python:3.12-slim) (45 min)
- [ ] Write `docker-compose.yml` with api + db + frontend services and health checks (1h)
- [ ] Write `entrypoint.sh` — run migrations then start uvicorn (20 min)
- [ ] Bootstrap GitHub Actions CI workflow (1h)

### Testing Tasks
- [ ] `test_create_category` — POST returns 201 with correct body (30 min)
- [ ] `test_duplicate_category_slug` — second POST with same slug returns 409 (20 min)
- [ ] `test_get_category_not_found` — GET /categories/999 returns 404 (15 min)
- [ ] `test_create_product_success` — POST with valid category_id returns 201 (30 min)
- [ ] `test_create_product_invalid_category` — POST with non-existent category_id returns 404 (20 min)
- [ ] `test_update_product` — PUT returns 200 with updated fields (25 min)
- [ ] `test_delete_product` — DELETE returns 204, subsequent GET returns 404 (20 min)
- [ ] `test_list_products_empty` — GET on empty DB returns `[]` (10 min)

### Architecture Improvements
- [ ] Document ADR-001: "Use SQLAlchemy async engine with asyncpg over sync SQLAlchemy" — reason: FastAPI is ASGI, blocking DB calls block the event loop
- [ ] Document ADR-002: "Use Alembic for migrations" — reason: programmatic control, version-controlled schema history

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 1 | Project scaffolding & repo setup | 5h |
| 2 | SQLAlchemy models & Alembic migrations | 5h |
| 3 | CRUD endpoints for Category and Product | 5.5h |
| 4 | Docker & Docker Compose | 5h |
| 5 | React product list & category list UI | 5h |
| 6 | Integration tests setup | 5h |
| 7 | Polish, CORS, structlog & CI skeleton | 4.5h |
| **Total** | | **~35h** |

### Expected Deliverables
- [ ] `docker compose up` starts React + FastAPI + PostgreSQL
- [ ] `/api/v1/products` and `/api/v1/categories` CRUD endpoints working
- [ ] React UI lists products and categories, supports create/delete
- [ ] 8 passing integration tests
- [ ] GitHub Actions CI runs ruff, mypy, pytest on push

### Definition of Done
- [ ] All 8 integration tests pass in CI
- [ ] `docker compose up --build` works from a clean checkout
- [ ] `/docs` Swagger UI is accessible and all endpoints documented
- [ ] No ruff or mypy errors
- [ ] React app loads in browser without console errors

### Pitfalls to Avoid
- Do not use synchronous `create_engine` — FastAPI is async; always use `create_async_engine`
- Do not forget `await session.commit()` after writes — async sessions do not auto-commit
- Do not put the DB URL directly in code — always use `pydantic-settings` with `.env`
- Do not skip the `health check` on the db service in Docker Compose — the API will fail on startup if Postgres isn't ready

### Interview Readiness
- What is ASGI vs WSGI and why does FastAPI require ASGI?
- How does SQLAlchemy async session differ from sync session?
- What is Alembic and what problem does it solve?
- Explain the difference between `Pydantic` schema and `SQLAlchemy` model
- What does `response_model` do in FastAPI?
- How does Docker Compose networking work — how does `api` container resolve `db`?

---

## Phase 2: Days 8–15 — Layered Architecture & Authentication

**Phase objective:** Refactor the naive CRUD into a layered router→service→repository→model architecture, implement JWT-based authentication with refresh tokens, add role-based access control (customer, seller, admin), and harden the API with middleware.

---

### Project Architecture

**Architecture style:** Modular monolith

**What changed from Phase 1:**
- Added: `User` model, auth endpoints (`/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`)
- Added: JWT access + refresh token flow
- Added: Role-based access control middleware
- Added: Request ID middleware (previously stubbed, now complete)
- Refactored: flat endpoint files → router/service/repository layers

**System diagram (end of Phase 2):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token header
    ↓
[FastAPI Monolith :8000]
    ├── /auth/*  → AuthRouter → AuthService → UserRepository
    ├── /products/* → ProductRouter → ProductService → ProductRepository
    └── /categories/* → CategoryRouter → CategoryService → CategoryRepository
         | SQL async (asyncpg)
         ↓
[PostgreSQL :5432]
    └── tables: users, products, categories, refresh_tokens

[Docker Compose wraps all above]
```

**Data flow — Login + protected resource request:**
1. React → POST /auth/login (email, password)
2. FastAPI AuthRouter → AuthService.login()
3. AuthService → UserRepository.get_by_email() → SQL SELECT WHERE email=?
4. AuthService verifies bcrypt hash → creates JWT access token (15 min) + refresh token (7 days)
5. Refresh token saved to `refresh_tokens` table (SQL INSERT)
6. Response: `{access_token, refresh_token, token_type}`
7. React stores tokens in memory (access) and httpOnly cookie (refresh)
8. React → GET /products (Authorization: Bearer <access_token>)
9. FastAPI `get_current_user` dependency decodes JWT → extracts user_id + role
10. Dependency injects user into route handler → response returned

---

### Business Features
- [ ] Users can register with email + password
- [ ] Users can log in and receive JWT access + refresh tokens
- [ ] Access token auto-refreshes via refresh endpoint
- [ ] Users can log out (refresh token revoked)
- [ ] Protected endpoints require valid JWT
- [ ] Admin-only endpoints reject customers with 403

---

#### Day 8 — Layered architecture refactor
**Daily Time Budget: ~5.5h**

- [ ] Create `app/repositories/` directory — write `base.py` with generic `BaseRepository[T]` with `get`, `get_all`, `create`, `update`, `delete` methods typed with generics (1.5h)
- [ ] Write `app/repositories/product_repository.py` — extend `BaseRepository`, move DB logic from router into repository methods (45 min)
- [ ] Write `app/repositories/category_repository.py` — same pattern (30 min)
- [ ] Create `app/services/` directory — write `product_service.py` — calls repository, applies business logic, raises domain exceptions (45 min)
- [ ] Write `app/services/category_service.py` — same pattern (30 min)
- [ ] Refactor `app/api/products.py` — routers now call service, not DB directly (30 min)
- [ ] Refactor `app/api/categories.py` — same (20 min)
- [ ] Run existing tests — confirm all still pass after refactor (30 min)

---

#### Day 9 — User model & password hashing
**Daily Time Budget: ~5h**

- [ ] Install `passlib[bcrypt]` and `pyjwt` — use `pyjwt`, NOT `python-jose` which is unmaintained and has unpatched CVEs as of 2024 (15 min)
- [ ] Write `app/models/user.py` — `User` model: `id`, `email` (unique), `hashed_password`, `role` (Enum: customer/seller/admin), `is_active`, timestamps (45 min)
- [ ] Write `app/models/refresh_token.py` — `RefreshToken`: `id`, `user_id` FK, `token` (unique), `expires_at`, `revoked` (30 min)
- [ ] Generate Alembic migration: `alembic revision --autogenerate -m "add users and refresh tokens"` — review and run (30 min)
- [ ] Write `app/core/security.py` — `hash_password(plain)`, `verify_password(plain, hashed)`, `create_access_token(data, expires_delta)`, `create_refresh_token()`, `decode_access_token(token)` using `jwt.encode/decode` from `pyjwt` (1.5h)
- [ ] Write unit tests for all security functions in `tests/test_security.py` (45 min)

---

#### Day 10 — Auth endpoints: register & login
**Daily Time Budget: ~5h**

- [ ] Write `app/repositories/user_repository.py` — `get_by_email`, `get_by_id`, `create`, `get_refresh_token`, `save_refresh_token`, `revoke_refresh_token` (45 min)
- [ ] Write `app/services/auth_service.py` — `register(email, password, role)`, `login(email, password)` → returns `TokenPair` (1h)
- [ ] Write `app/api/auth.py` — `POST /auth/register`, `POST /auth/login`, attach router to app (45 min)
- [ ] Write `app/schemas/auth.py` — `RegisterRequest`, `LoginRequest`, `TokenResponse`, `UserRead` (30 min)
- [ ] Test register → login flow manually via Swagger UI (20 min)
- [ ] Write `tests/test_auth.py` — test register success, duplicate email 409, login success, wrong password 401 (1h)

---

#### Day 11 — JWT dependency & protected routes
**Daily Time Budget: ~5h**

- [ ] Write `app/core/deps.py` — `get_current_user` FastAPI dependency: extract Bearer token from header, decode JWT, load user from DB, raise 401 if invalid/expired (1h)
- [ ] Write `require_role(*roles)` dependency factory — checks `current_user.role in roles`, raises 403 otherwise (45 min)
- [ ] Protect product write endpoints (POST, PUT, DELETE) with `require_role("admin", "seller")` (30 min)
- [ ] Protect category write endpoints with `require_role("admin")` (20 min)
- [ ] Add `GET /auth/me` endpoint — returns current user info (20 min)
- [ ] Test protected endpoints in Swagger UI — confirm 401 without token, 403 with wrong role, 200 with correct role (30 min)
- [ ] Write tests: `test_create_product_no_auth` → 401, `test_create_product_customer_role` → 403, `test_create_product_admin_role` → 201 (1h)

---

#### Day 12 — Refresh & logout endpoints
**Daily Time Budget: ~5h**

- [ ] Write `POST /auth/refresh` — validate refresh token from DB (not revoked, not expired), issue new access token, rotate refresh token (1.5h)
- [ ] Write `POST /auth/logout` — revoke refresh token (set `revoked=True` in DB) (30 min)
- [ ] Write tests: `test_refresh_success`, `test_refresh_with_revoked_token` → 401, `test_logout_then_refresh` → 401 (1h)
- [ ] Add `Depends(get_current_user)` to logout endpoint (15 min)
- [ ] Add token expiry cleanup task (mark as out-of-scope for now, document in TODO) (15 min)
- [ ] Update React: store access token in memory, store refresh token in httpOnly cookie via Set-Cookie header (1.5h)

---

#### Day 13 — CORS hardening & request middleware
**Daily Time Budget: ~4.5h**

- [ ] Move CORS allowed origins to settings — support comma-separated list from env var `CORS_ORIGINS` (30 min)
- [ ] Complete `X-Request-ID` middleware — if header present use it, else generate UUID4; bind to structlog context; return in response (45 min)
- [ ] Add `ProcessTimeMiddleware` — add `X-Process-Time` header to every response (30 min)
- [ ] Add rate limiting stub on `/auth/login` using in-memory counter (document that Redis-backed rate limiting comes in Phase 7) (45 min)
- [ ] Write middleware integration test — check `X-Request-ID` present in response headers (30 min)
- [ ] Update structlog to include `user_id` and `role` in log context after auth middleware resolves (30 min)
- [ ] Verify all logs include `request_id`, `user_id`, `method`, `path`, `status_code`, `duration_ms` (30 min)

---

#### Day 14 — React auth integration
**Daily Time Budget: ~5h**

- [ ] Create `src/context/AuthContext.tsx` — store `accessToken`, `user`, expose `login()`, `logout()`, `refreshToken()` (1.5h)
- [ ] Create `src/api/auth.ts` — `register()`, `login()`, `logout()`, `refresh()` API calls (45 min)
- [ ] Create `src/pages/LoginPage.tsx` and `RegisterPage.tsx` with forms (1h)
- [ ] Wrap Axios instance to inject `Authorization: Bearer <token>` header automatically (30 min)
- [ ] Add Axios response interceptor — on 401, attempt token refresh, retry original request once (1h)
- [ ] Test login → token refresh → logout flow in browser (15 min)

---

#### Day 15 — Full auth test suite & review
**Daily Time Budget: ~4.5h**

- [ ] Write `test_me_endpoint` — GET /auth/me with valid token returns user object (20 min)
- [ ] Write `test_access_token_expired` — mock expired token, confirm 401 (30 min)
- [ ] Write `test_refresh_token_rotation` — after refresh, old refresh token is revoked (30 min)
- [ ] Write `test_role_based_access` — table-driven test across all role/endpoint combos (1h)
- [ ] Run full test suite — fix any failures (30–60 min)
- [ ] Review security: confirm passwords never logged, tokens not stored in localStorage (30 min)
- [ ] Write ADR-003: "JWT access + DB-backed refresh token" — explain why stateless access + stateful refresh (30 min)

---

### Frontend Tasks
- [ ] Build `AuthContext` with login/logout/refresh state (1.5h)
- [ ] Build `LoginPage` and `RegisterPage` components (1h)
- [ ] Add Axios interceptor for token refresh on 401 (1h)
- [ ] Add route guards — redirect to `/login` if unauthenticated (30 min)
- [ ] Show current user name in navbar after login (20 min)

### Database Changes
- [ ] Add `users` table: `id`, `email` (unique), `hashed_password`, `role`, `is_active`, timestamps (30 min)
- [ ] Add `refresh_tokens` table: `id`, `user_id` FK, `token` (unique), `expires_at`, `revoked`, `created_at` (30 min)
- [ ] Index on `users.email` (unique index already from constraint) (10 min)
- [ ] Index on `refresh_tokens.token` (unique) and `refresh_tokens.user_id` (10 min)
- [ ] Alembic migration — review auto-generated, run against dev DB (20 min)

### DevOps & Infrastructure Tasks
- [ ] Add `SECRET_KEY`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` to `.env.example` (15 min)
- [ ] Update `docker-compose.yml` with new env vars (10 min)
- [ ] Confirm CI still passes after refactor (runs on Day 15) (20 min)

### Testing Tasks
- [ ] `test_register_success` — 201, user in DB (30 min)
- [ ] `test_register_duplicate_email` — 409 (20 min)
- [ ] `test_login_success` — 200, tokens in response (20 min)
- [ ] `test_login_wrong_password` — 401 (15 min)
- [ ] `test_protected_endpoint_no_token` — 401 (15 min)
- [ ] `test_protected_endpoint_wrong_role` — 403 (15 min)
- [ ] `test_refresh_success` — new access token returned (30 min)
- [ ] `test_refresh_revoked_token` — 401 (20 min)
- [ ] `test_logout_revokes_token` — logout then refresh → 401 (25 min)

### Architecture Improvements
- [ ] ADR-003: JWT access token (stateless, 15 min TTL) + DB-backed refresh token (stateful, 7-day TTL)
- [ ] ADR-004: Auth service will remain FastAPI throughout — never migrate to Django (document reasoning now as a reference)
- [ ] Introduce `BaseRepository[T]` generic to avoid copy-paste across repositories

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 8 | Layered architecture refactor | 5.5h |
| 9 | User model & password hashing | 5h |
| 10 | Auth endpoints: register & login | 5h |
| 11 | JWT dependency & protected routes | 5h |
| 12 | Refresh & logout endpoints | 5h |
| 13 | CORS hardening & request middleware | 4.5h |
| 14 | React auth integration | 5h |
| 15 | Full auth test suite & review | 4.5h |
| **Total** | | **~39.5h** |

### Expected Deliverables
- [ ] Register, login, refresh, logout endpoints working
- [ ] JWT auth protects all write endpoints
- [ ] Role-based access enforced on every route
- [ ] React login/register pages functional with token refresh
- [ ] 9 auth-specific integration tests passing

### Definition of Done
- [ ] All tests pass in CI (including new auth tests)
- [ ] `/auth/me` returns correct user for any valid token
- [ ] Expired token returns 401; wrong role returns 403
- [ ] Refresh token rotation works (old token revoked after refresh)
- [ ] Passwords never appear in logs or responses

### Pitfalls to Avoid
- Never store JWT access token in localStorage — XSS can steal it; use in-memory + httpOnly cookie for refresh
- Never return `hashed_password` in any API response — always use a response schema that excludes it
- Do not make access tokens long-lived to compensate for UX — fix the refresh flow instead
- Alembic `--autogenerate` does not detect all changes (e.g., server defaults on existing columns) — always review the migration file

### Interview Readiness
- Explain the difference between stateless JWT and stateful session tokens
- Why use a short-lived access token + long-lived refresh token instead of one long-lived token?
- What is RBAC and how did you implement it in FastAPI?
- How does bcrypt work and why not use MD5/SHA256 for passwords?
- What is the OAuth2 password flow vs authorization code flow?
- How would you invalidate all tokens for a user who changes their password?

---

## Phase 3: Days 16–23 — Sellers, Attributes, Variants & Inventory

**Phase objective:** Extend the product domain with seller profiles, product variants (size/color), an attribute system, and multi-warehouse stock tracking, while adopting bounded-context folder structure. Document the N+1 query problem by intentionally reproducing it.

---

### Project Architecture

**Architecture style:** Modular monolith (bounded contexts)

**What changed from Phase 2:**
- Added: `Seller` profile model linked to `User`
- Added: `ProductVariant`, `Attribute`, `AttributeValue` models
- Added: `Warehouse`, `Stock` models for multi-warehouse inventory
- Refactored: flat `app/models/` → bounded context folders `app/domains/catalog/`, `app/domains/auth/`, `app/domains/inventory/`

**System diagram (end of Phase 3):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token
    ↓
[FastAPI Monolith :8000]
    ├── domains/auth/      → users, refresh_tokens
    ├── domains/catalog/   → products, categories, variants, attributes
    └── domains/inventory/ → warehouses, stock
         | SQL async (asyncpg)
         ↓
[PostgreSQL :5432]
    └── tables: users, refresh_tokens, sellers, products, categories,
                product_variants, attributes, attribute_values,
                variant_attribute_values, warehouses, stock

[Docker Compose wraps all above]
```

**Data flow — Create Product with Variants (most complex new operation):**
1. Seller → POST /catalog/products (with variants array in body)
2. FastAPI → ProductService.create_with_variants()
3. ProductService → SellerRepository.get_by_user_id() → verify seller owns this request
4. ProductService → DB: INSERT INTO products (name, price, sku, category_id, seller_id)
5. For each variant: INSERT INTO product_variants (product_id, sku, price_delta)
6. For each attribute_value in variant: INSERT INTO variant_attribute_values
7. For each warehouse: INSERT INTO stock (variant_id, warehouse_id, quantity=0)
8. All above in ONE async transaction (committed together or rolled back)
9. Response: full product + variants + attribute values

---

### Business Features
- [ ] Sellers can register a seller profile linked to their user account
- [ ] Sellers can create products with multiple variants (e.g., T-shirt: S/M/L × Red/Blue)
- [ ] Each variant has its own SKU, price delta, and stock per warehouse
- [ ] Admin can manage warehouses
- [ ] Stock is tracked per variant per warehouse
- [ ] API consumers can query total available stock for a product across all warehouses

---

#### Day 16 — Bounded context folder restructure
**Daily Time Budget: ~5h**

- [ ] Create a root `Makefile` with targets: `make run`, `make test`, `make lint`, `make seed`, `make migrate` — document each target (20 min)
- [ ] Create `app/domains/` directory with `__init__.py` files (15 min)
- [ ] Create `app/domains/auth/` — move `models/user.py`, `models/refresh_token.py`, `repositories/user_repository.py`, `services/auth_service.py`, `api/auth.py`, `schemas/auth.py` (1h)
- [ ] Create `app/domains/catalog/` — move product and category files (45 min)
- [ ] Update all import paths throughout the codebase (1h)
- [ ] Run full test suite — confirm nothing broken by refactor (30–60 min)
- [ ] Create `app/domains/inventory/` as empty bounded context (10 min)
- [ ] Update `app/main.py` router includes to use new paths (20 min)

---

#### Day 17 — Seller profile & attribute models
**Daily Time Budget: ~5h**

- [ ] Write `app/domains/catalog/models/seller.py` — `Seller`: `id`, `user_id` (FK unique), `business_name`, `description`, `is_verified`, timestamps (30 min)
- [ ] Write `app/domains/catalog/models/attribute.py` — `Attribute`: `id`, `name` (e.g., "Color"), `slug`; `AttributeValue`: `id`, `attribute_id` FK, `value` (e.g., "Red") (45 min)
- [ ] Write `app/domains/catalog/models/product_variant.py` — `ProductVariant`: `id`, `product_id` FK, `sku` (unique), `price_delta` (Numeric, can be negative), `is_active`; M2M table `variant_attribute_values` linking variant to attribute_values (1h)
- [ ] Generate Alembic migration — review carefully: check FK chains (seller → user, variant → product, etc.) (45 min)
- [ ] Run migration and verify schema with `\d product_variants` (20 min)
- [ ] Write Pydantic schemas for `Seller`, `Attribute`, `AttributeValue`, `ProductVariantRead`, `ProductVariantCreate` (1h)

---

#### Day 18 — Inventory models & warehouses
**Daily Time Budget: ~5h**

- [ ] Write `app/domains/inventory/models/warehouse.py` — `Warehouse`: `id`, `name`, `location`, `is_active`, timestamps (30 min)
- [ ] Write `app/domains/inventory/models/stock.py` — `Stock`: `id`, `variant_id` FK, `warehouse_id` FK, `quantity` (Int, check >= 0), unique constraint on `(variant_id, warehouse_id)` (45 min)
- [ ] Generate and run Alembic migration for inventory tables (30 min)
- [ ] Write `WarehouseRepository` and `StockRepository` in inventory domain (45 min)
- [ ] Write `InventoryService.get_total_stock(variant_id)` — sums stock across all warehouses (30 min)
- [ ] Write `InventoryService.update_stock(variant_id, warehouse_id, delta)` — adds delta (can be negative for sales), raises if result < 0 (45 min)
- [ ] Write `app/domains/inventory/api/warehouses.py` — CRUD endpoints (admin only) (45 min)

---

#### Day 19 — Seller profile endpoints
**Daily Time Budget: ~5h**

- [ ] Write `SellerRepository` — `create`, `get_by_user_id`, `get_by_id`, `list_all` (30 min)
- [ ] Write `SellerService.register_seller(user_id, business_name, description)` — one user = one seller profile, raise conflict if exists (45 min)
- [ ] Write `app/domains/catalog/api/sellers.py` — `POST /sellers` (auth required, role=customer or seller), `GET /sellers/{id}`, `GET /sellers` (admin) (45 min)
- [ ] Add seller_id FK to `products` table — generate and run migration (30 min)
- [ ] Update `ProductService.create` to accept and store `seller_id`, verify current user is the seller (30 min)
- [ ] Write tests: `test_register_seller_success`, `test_register_seller_duplicate`, `test_seller_can_create_product`, `test_non_seller_cannot_create_product` (1.5h)

---

#### Day 20 — Product variants endpoints
**Daily Time Budget: ~5.5h**

- [ ] Write `ProductVariantRepository` — `create`, `get_by_product_id`, `get_by_id` (30 min)
- [ ] Write `ProductService.create_with_variants(product_data, variants)` — all in one transaction: create product, create variants, attach attribute values, create stock rows for all warehouses (2h)
- [ ] Write `POST /products/{id}/variants` endpoint — requires seller ownership check (1h)
- [ ] Write `GET /products/{id}/variants` — returns all variants with their attribute values (30 min)
- [ ] Test variant creation with 2 attributes × 3 values in Swagger UI (30 min)
- [ ] Write tests: `test_create_variant_success`, `test_create_variant_wrong_seller` → 403 (1h)

---

#### Day 21 — N+1 query problem: reproduce & document
**Daily Time Budget: ~5h**

- [ ] Seed database with 50 products, each with 3 variants, each variant with 2 attribute values (use a `scripts/seed.py` script) (1h)
- [ ] Write `GET /products` endpoint that fetches all products then lazily accesses `product.variants` for each — intentionally trigger N+1 (45 min)
- [ ] Enable SQLAlchemy query logging (`echo=True`) and observe 1 + N queries in logs (30 min)
- [ ] Write `docs/n_plus_one_problem.md` — show actual log output, explain why it happens (30 min)
- [ ] Fix with `selectinload` — add `options(selectinload(Product.variants).selectinload(ProductVariant.attribute_values))` to query (45 min)
- [ ] Compare query count before (51) and after (3) fix — document in `docs/n_plus_one_problem.md` (30 min)
- [ ] Write test that asserts `GET /products` response includes `variants` field (30 min)

---

#### Day 22 — Stock management endpoints
**Daily Time Budget: ~5h**

- [ ] Write `GET /inventory/stock?product_id=X` — returns stock per variant per warehouse (30 min)
- [ ] Write `PUT /inventory/stock/{variant_id}/{warehouse_id}` — admin/warehouse-manager sets absolute quantity (30 min)
- [ ] Write `POST /inventory/stock/{variant_id}/{warehouse_id}/adjust` — applies delta (positive for restock, negative for manual correction) (30 min)
- [ ] Add DB CHECK constraint `quantity >= 0` on stock table — verify migration (20 min)
- [ ] Write `InventoryService.reserve_stock(variant_id, warehouse_id, quantity)` — SELECT FOR UPDATE + check availability + UPDATE (will be used in checkout Phase 5) (1.5h)
- [ ] Write tests: `test_update_stock`, `test_adjust_stock_negative_to_zero_ok`, `test_adjust_stock_below_zero_fails` (1h)
- [ ] Manually test with Swagger: add stock to a warehouse, then adjust (30 min)

---

#### Day 23 — Full domain tests & CI update
**Daily Time Budget: ~4.5h**

- [ ] Write `test_full_product_lifecycle` — create category → create product → add variants → check stock → update stock (1.5h)
- [ ] Write `test_seller_isolation` — seller A cannot update seller B's product (30 min)
- [ ] Write `test_variant_attribute_values_returned` — GET /products includes correct attribute values on variants (30 min)
- [ ] Run `pytest -v --tb=short` — fix all failures (30–60 min)
- [ ] Run `ruff check` and `mypy` — fix any new errors from new files (30 min)
- [ ] Update `README.md` with bounded context folder structure diagram (20 min)

---

### Frontend Tasks
- [ ] Build `VariantSelector` component — dropdown per attribute (e.g., Color, Size) that selects a specific variant (1.5h)
- [ ] Update `ProductForm` to support adding variants with attribute values (1.5h)
- [ ] Display available stock per selected variant on product detail page (45 min)
- [ ] Build `SellerRegistrationPage` (30 min)

### Database Changes
- [ ] Add `sellers` table: id, user_id (FK unique), business_name, description, is_verified (30 min)
- [ ] Add `seller_id` FK to `products` table (20 min)
- [ ] Add `attributes` table: id, name, slug (30 min)
- [ ] Add `attribute_values` table: id, attribute_id FK, value (20 min)
- [ ] Add `product_variants` table: id, product_id FK, sku (unique), price_delta, is_active (30 min)
- [ ] Add `variant_attribute_values` M2M table: variant_id FK, attribute_value_id FK, unique constraint (20 min)
- [ ] Add `warehouses` table: id, name, location, is_active (20 min)
- [ ] Add `stock` table: id, variant_id FK, warehouse_id FK, quantity (check>=0), unique(variant_id, warehouse_id) (30 min)

### DevOps & Infrastructure Tasks
- [ ] Add `scripts/seed.py` — seeds 50 products with variants for N+1 demonstration (30 min)
- [ ] Update `docker-compose.yml` to mount seed script (10 min)
- [ ] Add `make seed` target in `Makefile` (10 min)

### Testing Tasks
- [ ] `test_create_attribute_and_value` — POST /attributes then POST /attributes/{id}/values (30 min)
- [ ] `test_create_product_with_variants` — POST /products with variants array (45 min)
- [ ] `test_seller_cannot_edit_others_product` — 403 response (20 min)
- [ ] `test_stock_update_success` (20 min)
- [ ] `test_stock_below_zero_rejected` (20 min)
- [ ] `test_n_plus_one_fixed` — assert GET /products makes ≤ 3 DB queries (using query counter hook) (45 min)

### Architecture Improvements
- [ ] Adopt bounded-context folder structure: `app/domains/{auth,catalog,inventory}/`
- [ ] ADR-005: "Bounded context separation within the monolith" — reason: prepares for microservices split in Phase 8
- [ ] Document N+1 problem and fix in `docs/n_plus_one_problem.md`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 16 | Bounded context folder restructure | 5h |
| 17 | Seller profile & attribute models | 5h |
| 18 | Inventory models & warehouses | 5h |
| 19 | Seller profile endpoints | 5h |
| 20 | Product variants endpoints | 5.5h |
| 21 | N+1 query problem: reproduce & document | 5h |
| 22 | Stock management endpoints | 5h |
| 23 | Full domain tests & CI update | 4.5h |
| **Total** | | **~40h** |

### Expected Deliverables
- [ ] Bounded context folder structure in place
- [ ] Sellers can create products with variants and attribute values
- [ ] Stock tracked per variant per warehouse
- [ ] N+1 problem documented and fixed with selectinload
- [ ] 6 new integration tests passing

### Definition of Done
- [ ] `POST /products` with `variants` array creates all rows in single transaction
- [ ] `GET /products` with 50 products makes ≤ 3 DB queries
- [ ] Stock adjustment below 0 returns 422 (DB constraint + service check)
- [ ] Seller A cannot modify Seller B's product (403)
- [ ] All tests pass in CI

### Pitfalls to Avoid
- Do not load variants/attributes lazily in list endpoints — always use `selectinload` explicitly
- Do not use separate transactions for product + variants — a failed variant insert must roll back the product
- Do not rely only on the DB CHECK constraint for stock ≥ 0 — validate in service layer too for better error messages
- Self-referential FK on categories (`parent_id`) requires `nullable=True` and careful migration order

### Interview Readiness
- Explain the N+1 query problem and how `selectinload` vs `joinedload` differ
- What is a bounded context in Domain-Driven Design?
- How do you model a M2M relationship in SQLAlchemy?
- Explain `SELECT FOR UPDATE` and when you'd use it
- What is a DB CHECK constraint and what layer should enforce it?
- How does a self-referential foreign key work in SQLAlchemy?

---

## Phase 4: Days 24–30 — Query Performance & Pagination

**Phase objective:** Profile and fix query performance issues, implement cursor-based pagination, add composite indexes with before/after EXPLAIN ANALYZE comparisons, and run first load tests with Locust.

---

### Project Architecture

**Architecture style:** Modular monolith (performance-hardened)

**What changed from Phase 3:**
- Added: Cursor-based pagination on all list endpoints
- Added: Composite indexes on `products`, `stock`, `product_variants`
- Added: Locust load testing scripts
- No new services or databases

**System diagram (end of Phase 4):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token
    ↓
[FastAPI Monolith :8000]
    ├── domains/auth/
    ├── domains/catalog/   ← cursor pagination, composite indexes
    └── domains/inventory/ ← stock query optimization
         | SQL async (asyncpg) — optimized queries with EXPLAIN
         ↓
[PostgreSQL :5432]
    └── composite indexes: (category_id, is_active, created_at)
                           (seller_id, is_active)
                           (variant_id, warehouse_id) [already unique]

[Locust :8089] ← load testing tool (dev only)

[Docker Compose wraps all above]
```

**Data flow — Cursor-paginated product list (most complex new operation):**
1. React → GET /products?limit=20&cursor=<base64_encoded_cursor>
2. FastAPI decodes cursor → extracts `(created_at, id)` of last seen row
3. ProductRepository builds query: `WHERE (created_at, id) < (cursor_created_at, cursor_id) ORDER BY created_at DESC, id DESC LIMIT 21`
4. Fetch 21 rows — if 21 returned, there is a next page (return first 20 + next_cursor)
5. Encode next cursor as base64 JSON `{created_at, id}`
6. Return `{items: [...20 products], next_cursor: "...", has_more: true}`

---

### Business Features
- [ ] All list endpoints support cursor-based pagination (`limit`, `cursor` params)
- [ ] Product list can be filtered by `category_id`, `seller_id`, `is_active`, `min_price`, `max_price`
- [ ] Filtering + pagination work together correctly
- [ ] API handles 500 concurrent users reading product list without timeouts (Locust baseline)

---

#### Day 24 — EXPLAIN ANALYZE baseline & index strategy
**Daily Time Budget: ~5h**

- [ ] Seed DB to 10,000 products with realistic data using `scripts/seed_large.py` (1h)
- [ ] Enable `pg_stat_statements` extension in PostgreSQL: add `shared_preload_libraries = 'pg_stat_statements'` to PostgreSQL config in `docker-compose.yml`, restart DB, run `CREATE EXTENSION pg_stat_statements;` — this tracks total execution time and call count per query (30 min)
- [ ] Run `EXPLAIN ANALYZE SELECT * FROM products WHERE category_id=1 AND is_active=true ORDER BY created_at DESC LIMIT 20` — save output to `docs/query_analysis/baseline_products.txt` (30 min)
- [ ] Run `EXPLAIN ANALYZE` for stock query: `SELECT SUM(quantity) FROM stock WHERE variant_id = ANY(...)` (30 min)
- [ ] Identify sequential scans in output — document which columns need indexes (30 min)
- [ ] Write Alembic migration: `CREATE INDEX idx_products_category_active_created ON products (category_id, is_active, created_at DESC)` (30 min)
- [ ] Write Alembic migration: `CREATE INDEX idx_products_seller_active ON products (seller_id, is_active)` (20 min)
- [ ] Run migration, re-run EXPLAIN ANALYZE — compare Index Scan vs Seq Scan (30 min)
- [ ] Save after-index output to `docs/query_analysis/after_index_products.txt` (10 min)
- [ ] Document cost reduction in `docs/query_analysis/analysis.md` (30 min)

---

#### Day 25 — Cursor-based pagination implementation
**Daily Time Budget: ~5h**

- [ ] Write `app/core/pagination.py` — `encode_cursor(created_at, id) → str`, `decode_cursor(cursor_str) → (datetime, uuid)` using base64 + JSON (1h)
- [ ] Write `PaginatedResponse[T]` generic Pydantic model: `items: list[T]`, `next_cursor: str | None`, `has_more: bool` (30 min)
- [ ] Update `ProductRepository.get_paginated(limit, cursor, filters)` — builds WHERE clause with keyset condition `(created_at, id) < (cursor_dt, cursor_id)` (1.5h)
- [ ] Update `GET /products` endpoint to accept `limit: int = 20, cursor: str | None = None` query params (30 min)
- [ ] Test cursor pagination manually: page 1 → get cursor → page 2 → verify no duplicates or gaps (30 min)
- [ ] Apply same cursor pagination to `GET /categories` (30 min)

---

#### Day 26 — Product filtering
**Daily Time Budget: ~5h**

- [ ] Write `ProductFilterParams` Pydantic model (as `Depends`): `category_id`, `seller_id`, `is_active`, `min_price`, `max_price`, `search` (partial name match) (45 min)
- [ ] Update `ProductRepository.get_paginated` to dynamically build WHERE conditions from filter params using SQLAlchemy `and_()` (1.5h)
- [ ] Add `CREATE INDEX idx_products_price ON products (price)` migration for price range queries (20 min)
- [ ] Test combinations: filter by category + price range + cursor pagination (30 min)
- [ ] Write tests: `test_filter_by_category`, `test_filter_by_price_range`, `test_filter_combined_with_pagination` (1h)
- [ ] Confirm EXPLAIN ANALYZE uses index for filtered + paginated queries (45 min)

---

#### Day 27 — Eager loading optimization for product detail
**Daily Time Budget: ~5h**

- [ ] Profile `GET /products/{id}` — count DB queries when returning product + variants + attribute values + stock (30 min)
- [ ] Add `joinedload` vs `selectinload` comparison: use `joinedload` for product→category (1:1), `selectinload` for product→variants (1:N) (1h)
- [ ] Update `ProductRepository.get_by_id_full` — load product with all relations in 2-3 queries max (1h)
- [ ] Add `GET /products/{id}/full` endpoint returning complete product with nested data (30 min)
- [ ] Write test asserting `GET /products/{id}/full` returns variants with attribute values in response (30 min)
- [ ] Document in `docs/query_analysis/eager_loading.md` — joinedload vs selectinload tradeoffs (1h)

---

#### Day 28 — Locust load testing setup
**Daily Time Budget: ~5h**

- [ ] Install `locust` in dev dependencies (10 min)
- [ ] Write `locustfiles/product_list.py` — `HttpUser` that hits `GET /products`, `GET /products?cursor=...`, `GET /products/{id}/full` with realistic think time (1.5h)
- [ ] Add `locust` service to `docker-compose.yml` (or run standalone) with web UI at :8089 (30 min)
- [ ] Run Locust at 50 users, ramp to 200 — observe response time percentiles (p50, p95, p99) and error rate (45 min)
- [ ] Save baseline metrics to `docs/load_tests/baseline_50_users.png` (screenshot) (15 min)
- [ ] Identify bottleneck — likely product list query (30 min)
- [ ] Tune `POOL_SIZE` and `MAX_OVERFLOW` in SQLAlchemy async engine based on connection pressure (45 min)
- [ ] Re-run Locust at 200 users — document improvement (30 min)

---

#### Day 29 — Connection pooling & slow query log
**Daily Time Budget: ~4.5h**

- [ ] Configure PostgreSQL `log_min_duration_statement = 100` in dev — enable slow query log (30 min)
- [ ] Run seed + Locust — inspect slow query log AND query `SELECT query, calls, total_exec_time/calls AS avg_ms FROM pg_stat_statements ORDER BY avg_ms DESC LIMIT 10` to find hottest queries (30 min)
- [ ] Fix any slow queries found: add missing indexes or rewrite with CTE if needed (1–2h)
- [ ] Configure SQLAlchemy pool: `pool_size=10`, `max_overflow=20`, `pool_timeout=30`, `pool_recycle=1800` (30 min)
- [ ] Write `GET /health` and `GET /ready` endpoints — health checks DB connection ping (30 min)
- [ ] Verify health endpoint responds correctly when DB is down (simulate by stopping db container) (30 min)

---

#### Day 30 — Pagination tests & phase review
**Daily Time Budget: ~4.5h**

- [ ] Write `test_cursor_pagination_no_gaps` — fetch all 100 seeded products using cursor, verify count (45 min)
- [ ] Write `test_cursor_pagination_stable` — two concurrent requests with same cursor return same results (30 min)
- [ ] Write `test_filter_and_paginate_combined` (30 min)
- [ ] Write `test_index_used_for_category_filter` — use `EXPLAIN` output from DB to assert no seq scan (30–60 min)
- [ ] Run full test suite — confirm all pass (30 min)
- [ ] Write ADR-006: "Cursor-based pagination over offset" — explain why offset pagination breaks at scale (30 min)
- [ ] Update `README.md` with pagination API docs (20 min)

---

### Frontend Tasks
- [ ] Add "Load More" button that fetches next page using `next_cursor` from response (45 min)
- [ ] Add filter sidebar: category dropdown, price range inputs, active toggle (1h)
- [ ] Debounce filter inputs with 300ms delay before firing API call (30 min)
- [ ] Show loading skeleton while fetching (30 min)

### Database Changes
- [ ] `CREATE INDEX idx_products_category_active_created ON products (category_id, is_active, created_at DESC)` (20 min)
- [ ] `CREATE INDEX idx_products_seller_active ON products (seller_id, is_active)` (15 min)
- [ ] `CREATE INDEX idx_products_price ON products (price)` (10 min)
- [ ] Document each index with rationale in migration comment (15 min)

### DevOps & Infrastructure Tasks
- [ ] Write `scripts/seed_large.py` — 10,000 products with Faker library (45 min)
- [ ] Add `locust` service to `docker-compose.yml` (20 min)
- [ ] Add `make load-test` Makefile target (10 min)
- [ ] Configure PostgreSQL slow query log in `docker-compose.yml` via command args (20 min)

### Testing Tasks
- [ ] `test_cursor_no_gaps` — paginate all items, verify total count (45 min)
- [ ] `test_cursor_stable_ordering` — same cursor = same page (30 min)
- [ ] `test_filter_by_category_and_price` (25 min)
- [ ] `test_filter_empty_result` — valid filters with no matching products returns empty list (20 min)
- [ ] `test_health_endpoint_db_up` (15 min)
- [ ] `test_health_endpoint_db_down` — mock DB failure (30 min)

### Architecture Improvements
- [ ] ADR-006: Cursor-based pagination vs offset-based
- [ ] Document composite index strategy in `docs/query_analysis/index_strategy.md`
- [ ] Document eager loading strategy per relationship type

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 24 | EXPLAIN ANALYZE baseline & index strategy | 5h |
| 25 | Cursor-based pagination implementation | 5h |
| 26 | Product filtering | 5h |
| 27 | Eager loading optimization | 5h |
| 28 | Locust load testing setup | 5h |
| 29 | Connection pooling & slow query log | 4.5h |
| 30 | Pagination tests & phase review | 4.5h |
| **Total** | | **~34h** |

### Expected Deliverables
- [ ] All list endpoints use cursor-based pagination
- [ ] Product list supports 5 filter dimensions simultaneously
- [ ] Composite indexes in place with documented before/after EXPLAIN output
- [ ] Locust baseline at 200 users documented
- [ ] Health and readiness endpoints working

### Definition of Done
- [ ] `GET /products` with 10k rows returns in < 50ms (p95) at 200 concurrent users
- [ ] Cursor pagination produces zero gaps or duplicates over 10k products
- [ ] EXPLAIN ANALYZE shows Index Scan (not Seq Scan) for category filter query
- [ ] All 6 new tests pass

### Pitfalls to Avoid
- Cursor pagination requires a stable sort key — `(created_at, id)` works; `created_at` alone can have ties
- `joinedload` on a 1:N produces a JOIN that multiplies rows — use `selectinload` instead for collections
- Connection pool size must not exceed `max_connections` in PostgreSQL (default 100) — leave headroom for admin connections
- Locust workers share connections — set `pool_size` per worker, not total

### Interview Readiness
- Why is cursor pagination better than OFFSET for large tables?
- Explain `EXPLAIN ANALYZE` output — what is a Seq Scan vs Index Scan vs Bitmap Heap Scan?
- What is a composite index and how does column order matter?
- Explain `joinedload` vs `selectinload` in SQLAlchemy — when to use each?
- What is connection pooling and what happens when the pool is exhausted?
- How do you find slow queries in PostgreSQL?

---

## Phase 5: Days 31–38 — Cart, Checkout & Transactional Integrity

**Phase objective:** Build cart CRUD and a checkout flow with pessimistic locking (SELECT FOR UPDATE), implement the Unit of Work pattern, and write concurrency race-condition tests using 20 simultaneous checkout requests.

---

### Project Architecture

**Architecture style:** Modular monolith with async workers (stub)

**What changed from Phase 4:**
- Added: `Cart`, `CartItem` models
- Added: `Order`, `OrderItem` models (stub — full order in Phase 6)
- Added: `domains/orders/` bounded context
- Added: Pessimistic locking in checkout flow
- Added: Unit of Work pattern around checkout transaction

**System diagram (end of Phase 5):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token
    ↓
[FastAPI Monolith :8000]
    ├── domains/auth/
    ├── domains/catalog/
    ├── domains/inventory/  ← SELECT FOR UPDATE on stock rows
    └── domains/orders/     ← Cart, CartItem, Order, OrderItem
         | SQL async (asyncpg) — transactions with FOR UPDATE
         ↓
[PostgreSQL :5432]
    └── tables: + carts, cart_items, orders, order_items

[Docker Compose wraps all above]
```

**Data flow — Checkout (most complex new operation):**
1. Customer → POST /checkout (cart_id, shipping_address)
2. FastAPI → CheckoutService.checkout(user_id, cart_id)
3. Unit of Work begins: single async DB transaction
4. CartRepository.get_with_items(cart_id) — verify cart belongs to user
5. For each cart_item: StockRepository.lock_variant(variant_id, warehouse_id) → SELECT ... FOR UPDATE NOWAIT
6. If any row locked by another transaction → raises 409 (conflict, try again)
7. For each item: verify stock.quantity >= requested_quantity — raise 422 if not
8. OrderRepository.create(user_id, items, total) — INSERT order + order_items
9. For each item: UPDATE stock SET quantity = quantity - N WHERE variant_id=... (same TX)
10. CartRepository.clear(cart_id) — DELETE cart_items (same TX)
11. COMMIT — all above succeed atomically
12. Response: order_id, total, status=PENDING

---

### Business Features
- [ ] Customers can add/remove/update items in their cart
- [ ] Cart persists across sessions (DB-backed)
- [ ] Checkout creates an order and reserves stock atomically
- [ ] Two users buying the last item simultaneously — only one succeeds
- [ ] Cart is cleared on successful checkout

---

#### Day 31 — Cart models & CRUD
**Daily Time Budget: ~5h**

- [ ] Write `app/domains/orders/models/cart.py` — `Cart`: id, user_id FK (unique — one cart per user), created_at; `CartItem`: id, cart_id FK, variant_id FK, quantity, unique(cart_id, variant_id) (45 min)
- [ ] Generate and run Alembic migration (20 min)
- [ ] Write `CartRepository` — `get_or_create_for_user`, `add_item(cart_id, variant_id, quantity)`, `update_item_quantity`, `remove_item`, `get_with_items`, `clear` (1.5h)
- [ ] Write `CartService` — wraps repository, validates variant exists and is_active before adding (45 min)
- [ ] Write `app/domains/orders/api/cart.py` — `GET /cart`, `POST /cart/items`, `PUT /cart/items/{variant_id}`, `DELETE /cart/items/{variant_id}` (all require auth) (1h)
- [ ] Test all cart endpoints in Swagger UI (30 min)

---

#### Day 32 — Order models
**Daily Time Budget: ~5h**

- [ ] Write `app/domains/orders/models/order.py` — `Order`: id, user_id FK, status (Enum: PENDING/CONFIRMED/CANCELLED/SHIPPED/DELIVERED), total (Numeric), shipping_address (JSON), created_at; `OrderItem`: id, order_id FK, variant_id FK, quantity, unit_price (1h)
- [ ] Generate and run Alembic migration for orders (20 min)
- [ ] Write `OrderRepository` — `create(user_id, items, total, address)`, `get_by_id`, `get_by_user`, `update_status` (1h)
- [ ] Write Pydantic schemas: `OrderCreate`, `OrderRead`, `OrderItemRead` (30 min)
- [ ] Write `GET /orders` (paginated, user's own orders) and `GET /orders/{id}` endpoints (45 min)
- [ ] Write test: `test_get_empty_orders_list` (15 min)
- [ ] Write test: `test_order_belongs_to_user` — user A cannot see user B's order (30 min)

---

#### Day 33 — Unit of Work pattern
**Daily Time Budget: ~5.5h**

- [ ] Write `app/core/unit_of_work.py` — `UnitOfWork` async context manager that holds one `AsyncSession`, exposes `async with uow: ... await uow.commit()` (1.5h)
- [ ] Attach all repositories as properties on UoW: `uow.cart`, `uow.orders`, `uow.stock` (30 min)
- [ ] Refactor `CheckoutService` to accept and use `UnitOfWork` instead of raw session (1h)
- [ ] Write test: `test_unit_of_work_rollback_on_exception` — verify that an exception mid-checkout rolls back all changes (1h)
- [ ] Document UoW pattern in `docs/patterns/unit_of_work.md` (45 min)

---

#### Day 34 — Checkout with SELECT FOR UPDATE
**Daily Time Budget: ~5.5h**

- [ ] Write `StockRepository.lock_and_get(variant_id, warehouse_id)` — `SELECT * FROM stock WHERE variant_id=? AND warehouse_id=? FOR UPDATE NOWAIT` using SQLAlchemy `with_for_update(nowait=True)` (1h)
- [ ] Write `CheckoutService.checkout(user_id, cart_id, shipping_address)` — full transaction: lock stocks → validate quantities → create order → decrement stocks → clear cart → commit (2h)
- [ ] Write `POST /checkout` endpoint — calls `CheckoutService.checkout`, returns 201 with order (30 min)
- [ ] Test happy path: add 2 items to cart → checkout → verify order created and stock decremented (45 min)
- [ ] Test insufficient stock: set stock to 1, try to checkout with quantity 2 → 422 (30 min)

---

#### Day 35 — Race condition test: 20 concurrent checkouts
**Daily Time Budget: ~5h**

- [ ] Set stock quantity to 1 for a specific variant (1 unit available) (15 min)
- [ ] Write `tests/test_checkout_concurrency.py` — spin up 20 asyncio tasks, each attempting to checkout that variant simultaneously using `asyncio.gather(*[checkout() for _ in range(20)])` (1.5h)
- [ ] Assert exactly 1 checkout succeeds (200/201) and 19 fail with 409 (locked) or 422 (out of stock) (30 min)
- [ ] Assert final stock quantity is 0 (no over-selling) (15 min)
- [ ] Run test 5 times — confirm consistent results (no flakiness) (30 min)
- [ ] Document race condition test in `docs/patterns/concurrency_checkout.md` (1h)
- [ ] Handle `OperationalError` from `NOWAIT` lock failure — catch and convert to HTTP 409 with `Retry-After` header (30 min)

---

#### Day 36 — Cart edge cases & validation
**Daily Time Budget: ~5h**

- [ ] Handle `POST /cart/items` when item already exists — update quantity instead of duplicating (30 min)
- [ ] Add `max_quantity_per_item=100` validation — return 422 if exceeded (20 min)
- [ ] Add check: cannot add inactive variant to cart → 422 (20 min)
- [ ] Write `CartService.validate_cart_for_checkout()` — checks all cart items still have sufficient stock before attempting checkout (45 min)
- [ ] Call `validate_cart_for_checkout` before entering the locking transaction to give early user-friendly errors (30 min)
- [ ] Write tests: `test_cart_add_duplicate_item_updates_quantity`, `test_cart_rejects_inactive_variant`, `test_checkout_validates_stock_before_locking` (1h)
- [ ] Update React cart page to show stock availability warnings (1h)

---

#### Day 37 — React checkout flow
**Daily Time Budget: ~5h**

- [ ] Build `CartPage.tsx` — list cart items, quantity controls, remove buttons, subtotal (1.5h)
- [ ] Build `CheckoutPage.tsx` — shipping address form, order summary, checkout button (1h)
- [ ] Handle 409 conflict response in React — show "This item was just purchased by someone else. Please refresh." (30 min)
- [ ] Handle 422 insufficient stock — show per-item stock warnings (30 min)
- [ ] On successful checkout redirect to `OrderConfirmationPage.tsx` with order details (45 min)
- [ ] Test checkout flow end-to-end in browser (30 min)

---

#### Day 38 — Full test suite & phase review
**Daily Time Budget: ~4.5h**

- [ ] Write `test_checkout_clears_cart` — verify cart_items deleted after successful checkout (20 min)
- [ ] Write `test_checkout_with_multiple_items` — 3 different variants in cart, all succeed (30 min)
- [ ] Write `test_concurrent_checkout_no_oversell` — the race condition test (already written Day 35, finalize) (30 min)
- [ ] Run full test suite `pytest -v` — all must pass (30–60 min)
- [ ] Run `ruff check` and `mypy` — fix errors (30 min)
- [ ] Write ADR-007: "Pessimistic locking for checkout" — why not optimistic locking here (30 min)
- [ ] Write ADR-008: "Unit of Work pattern for multi-repository transactions" (30 min)

---

### Frontend Tasks
- [ ] Build `CartPage` with item list, quantity controls, subtotal (1.5h)
- [ ] Build `CheckoutPage` with address form and order summary (1h)
- [ ] Build `OrderConfirmationPage` with order details (30 min)
- [ ] Handle 409 and 422 errors with user-friendly messages (30 min)
- [ ] Show cart item count in navbar (20 min)

### Database Changes
- [ ] Add `carts` table: id, user_id (FK unique), created_at (20 min)
- [ ] Add `cart_items` table: id, cart_id FK, variant_id FK, quantity, unique(cart_id, variant_id) (25 min)
- [ ] Add `orders` table: id, user_id FK, status, total, shipping_address (JSON), created_at (30 min)
- [ ] Add `order_items` table: id, order_id FK, variant_id FK, quantity, unit_price (25 min)
- [ ] Index on `orders.user_id` for user order history queries (10 min)

### DevOps & Infrastructure Tasks
- [ ] No new services — only ensure `docker compose up` still works (15 min)

### Testing Tasks
- [ ] `test_add_to_cart` — POST /cart/items → 201 (20 min)
- [ ] `test_add_duplicate_updates_quantity` (20 min)
- [ ] `test_checkout_success` — full happy path (45 min)
- [ ] `test_checkout_insufficient_stock` — 422 (20 min)
- [ ] `test_concurrent_checkout_no_oversell` — 20 concurrent asyncio tasks, 1 item (1.5h)
- [ ] `test_checkout_clears_cart` (20 min)
- [ ] `test_order_isolation_between_users` (25 min)

### Architecture Improvements
- [ ] ADR-007: Pessimistic locking (SELECT FOR UPDATE NOWAIT) over optimistic locking for checkout
- [ ] ADR-008: Unit of Work pattern for checkout transaction
- [ ] Document concurrency strategy in `docs/patterns/`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 31 | Cart models & CRUD | 5h |
| 32 | Order models | 5h |
| 33 | Unit of Work pattern | 5.5h |
| 34 | Checkout with SELECT FOR UPDATE | 5.5h |
| 35 | Race condition test: 20 concurrent checkouts | 5h |
| 36 | Cart edge cases & validation | 5h |
| 37 | React checkout flow | 5h |
| 38 | Full test suite & phase review | 4.5h |
| **Total** | | **~40.5h** |

### Expected Deliverables
- [ ] Cart CRUD API working
- [ ] Checkout atomically decrements stock and creates order
- [ ] Race condition test: 1 out of 20 concurrent checkouts wins, stock never goes negative
- [ ] React cart and checkout pages functional

### Definition of Done
- [ ] Concurrent checkout test passes 5/5 runs with no overselling
- [ ] `POST /checkout` is atomic — partial failures roll back completely
- [ ] All 7 new tests pass in CI

### Pitfalls to Avoid
- `FOR UPDATE NOWAIT` raises an exception immediately if row is locked — catch `OperationalError` specifically
- Do not validate stock before beginning the transaction and then lock inside — always lock first, then validate
- Unit of Work must use a single session for all operations in the transaction — do not open multiple sessions
- Cart items quantity must be validated at checkout time, not just at add-to-cart time (stock may have changed)

### Interview Readiness
- Explain pessimistic vs optimistic locking — when to choose each
- What is `SELECT FOR UPDATE NOWAIT` and how does it differ from `SELECT FOR UPDATE`?
- What is the Unit of Work pattern and what problem does it solve?
- How do you test concurrent operations in pytest-asyncio?
- What happens if a transaction is rolled back — are all statements undone?
- Explain lost update anomaly — how does `FOR UPDATE` prevent it?

---

## Phase 6: Days 39–46 — Orders, Payments & Outbox Pattern

**Phase objective:** Build the order state machine, implement idempotent payment flow with idempotency keys, and apply the Transactional Outbox pattern to reliably publish events in the same DB transaction as the business write.

---

### Project Architecture

**Architecture style:** Modular monolith with outbox pattern

**What changed from Phase 5:**
- Added: `Payment` model, payment flow endpoints
- Added: `Outbox` table and relay job (polling-based, Kafka not yet)
- Added: Order state machine (PENDING→CONFIRMED→SHIPPED→DELIVERED/CANCELLED)
- Added: Audit log for order status changes
- Added: `IdempotencyKey` table for payment deduplication

**System diagram (end of Phase 6):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token
    ↓
[FastAPI Monolith :8000]
    ├── domains/auth/
    ├── domains/catalog/
    ├── domains/inventory/
    └── domains/orders/
         ├── Cart + Checkout (Phase 5)
         ├── Order State Machine
         ├── Payment flow (idempotency keys)
         └── Outbox relay (background asyncio task)
              | SQL async
              ↓
[PostgreSQL :5432]
    └── + payments, idempotency_keys, outbox_events, order_audit_log

[Docker Compose wraps all above]
```

**Data flow — Payment with Outbox (most complex new operation):**
1. Customer → POST /payments (order_id, idempotency_key, payment_method_token)
2. PaymentService checks `idempotency_keys` table — if key exists, return cached response immediately (no gateway call)
3. **Call payment gateway OUTSIDE the transaction** — `gateway.charge(amount, token)` → returns `{reference, status}` (this can take 1–3 seconds; holding a DB transaction open during this call would exhaust the connection pool)
4. PaymentService begins DB transaction (only after gateway call completes):
   a. INSERT INTO payments (order_id, amount, status=PROCESSING, gateway_reference)
   b. UPDATE payments SET status = SUCCESS/FAILED based on gateway result
   c. UPDATE orders SET status = CONFIRMED (if success)
   d. INSERT INTO outbox_events (aggregate_type='order', aggregate_id, event_type='OrderConfirmed', payload)
   e. INSERT INTO idempotency_keys (key, response_snapshot)
5. COMMIT — all 5 writes atomic (gateway result is already known before TX opens)
6. Background outbox relay polls `outbox_events WHERE published=false` → publishes to stub broker → marks published
7. Response to client: payment result

> **Why this order matters:** If the gateway call is inside the transaction, a 2-second gateway response holds a DB connection for 2 seconds. At 50 concurrent payments, that's 100 seconds of connection-time blocked. Keep IO-bound external calls outside transactions.

---

### Business Features
- [ ] Customers can pay for an order with an idempotency key (safe to retry)
- [ ] Duplicate payment requests with same idempotency key return cached result
- [ ] Order transitions through states: PENDING → CONFIRMED → SHIPPED → DELIVERED
- [ ] Admin can cancel an order (transitions to CANCELLED, stock is returned)
- [ ] Every order status change is logged to audit table with who changed it and when

---

#### Day 39 — Order state machine
**Daily Time Budget: ~5h**

- [ ] Define `OrderStatus` Enum: PENDING, CONFIRMED, CANCELLED, SHIPPED, DELIVERED (15 min)
- [ ] Write `OrderStateMachine` class in `app/domains/orders/state_machine.py` — define allowed transitions as dict: `{PENDING: [CONFIRMED, CANCELLED], CONFIRMED: [SHIPPED, CANCELLED], SHIPPED: [DELIVERED]}` (1h)
- [ ] Write `OrderStateMachine.transition(current, next)` — raises `InvalidTransitionError` if not allowed (30 min)
- [ ] Add `PUT /orders/{id}/status` endpoint (admin only) — calls state machine, updates DB, writes audit log entry (45 min)
- [ ] Write `order_audit_log` model: `id`, `order_id` FK, `from_status`, `to_status`, `changed_by` (user_id FK), `changed_at`, `note` (30 min)
- [ ] Generate migration and run (20 min)
- [ ] Write tests: `test_valid_transition`, `test_invalid_transition_raises`, `test_audit_log_written_on_status_change` (1h)

---

#### Day 40 — Payment model & idempotency keys
**Daily Time Budget: ~5.5h**

- [ ] Write `app/domains/orders/models/payment.py` — `Payment`: id, order_id FK (unique), amount (Numeric), status (Enum: PROCESSING/SUCCESS/FAILED/REFUNDED), gateway_reference, created_at (30 min)
- [ ] Write `IdempotencyKey` model: id, key (unique), user_id FK, response_status_code, response_body (JSON), created_at, expires_at (30 min)
- [ ] Generate and run Alembic migration (20 min)
- [ ] Write `IdempotencyService.get_or_create(key, user_id)` — returns cached response if key exists and not expired (1.5h)
- [ ] Write `PaymentRepository` — create, get_by_order, update_status (30 min)
- [ ] Write Pydantic schemas: `PaymentRequest` (includes `idempotency_key` header), `PaymentResponse` (45 min)

---

#### Day 41 — Mock payment gateway & payment endpoint
**Daily Time Budget: ~5h**

- [ ] Write `app/services/payment_gateway.py` — `MockPaymentGateway.charge(amount, token)` — randomly succeeds 90% / fails 10%, returns `{reference, status}` (simulate latency with `asyncio.sleep(0.3)` to mimic a real gateway) (45 min)
- [ ] Write `PaymentService.process_payment(order_id, user_id, idempotency_key, token)` — correct order: 1) check idempotency key, 2) call gateway OUTSIDE transaction, 3) open transaction, 4) write payment + order status + outbox event + idempotency record, 5) commit (2h)
- [ ] Write `POST /payments` endpoint — reads `Idempotency-Key` from request header, calls service (45 min)
- [ ] Test: pay for an order → verify order transitions to CONFIRMED (30 min)
- [ ] Test: submit same payment twice with same idempotency key → second response matches first, no duplicate payment row (30 min)
- [ ] Test: pay for cancelled order → 422 (invalid state) (20 min)

---

#### Day 42 — Outbox pattern implementation
**Daily Time Budget: ~5.5h**

- [ ] Write `OutboxEvent` model: `id`, `aggregate_type`, `aggregate_id`, `event_type`, `payload` (JSON), `published` (bool), `created_at`, `published_at` (30 min)
- [ ] Generate and run migration (15 min)
- [ ] Write `OutboxRepository.create_event(event_type, aggregate_type, aggregate_id, payload)` — INSERT in same transaction as business write (45 min)
- [ ] Update `PaymentService.process_payment` to INSERT outbox event in same transaction as payment + order update (1h)
- [ ] Write `OutboxRelay` — background asyncio task (using `asyncio.create_task`) that polls `SELECT * FROM outbox_events WHERE published=false ORDER BY created_at LIMIT 10`, "publishes" to stdout/log for now, then marks published=true (1.5h)
- [ ] Start `OutboxRelay` in `app/main.py` `startup` event (20 min)
- [ ] Write test: `test_outbox_event_created_on_payment` — verify outbox row exists after payment (30 min)

---

#### Day 43 — Order cancellation & stock return
**Daily Time Budget: ~5h**

- [ ] Write `OrderService.cancel_order(order_id, user_id, note)` — admin or order owner can cancel; transitions state machine to CANCELLED; returns stock (1.5h)
- [ ] Stock return: for each order_item, UPDATE stock SET quantity = quantity + item.quantity WHERE variant_id=... (same transaction) (45 min)
- [ ] Write `POST /orders/{id}/cancel` endpoint — calls service, requires auth (30 min)
- [ ] Add cancellation outbox event: `OrderCancelled` with order payload (20 min)
- [ ] Write tests: `test_cancel_order_returns_stock`, `test_cancel_confirmed_order_ok`, `test_cancel_shipped_order_forbidden` → 422 (1h)
- [ ] Handle idempotent cancel — cancelling an already-cancelled order returns 200 not 422 (30 min)

---

#### Day 44 — Admin order management dashboard
**Daily Time Budget: ~5h**

- [ ] Write `GET /admin/orders` — paginated list with filters: status, user_id, date range (admin only) (45 min)
- [ ] Write `GET /admin/orders/{id}` — full order detail including items, payment, audit log (30 min)
- [ ] Build `AdminOrdersPage.tsx` in React — list with status filter, click to view detail (1.5h)
- [ ] Build `OrderDetailPage.tsx` — show order items, payment status, audit log timeline (1.5h)
- [ ] Test filtering by status in browser (30 min)

---

#### Day 45 — Outbox relay hardening & integration test
**Daily Time Budget: ~5h**

- [ ] Add error handling to `OutboxRelay` — if publishing fails, log error and skip (will retry on next poll) (30 min)
- [ ] Add `retry_count` column to `outbox_events` — increment on failure, skip after 3 retries (45 min)
- [ ] Write `test_outbox_relay_marks_published` — create outbox event, run relay tick, verify `published=true` (30 min)
- [ ] Write `test_outbox_payment_idempotency` — full test: checkout → pay → pay again with same key → verify 1 payment row, 1 outbox event (1h)
- [ ] Write `test_stock_returned_on_cancel` — checkout → cancel → verify stock quantity restored (45 min)
- [ ] Run full test suite (30–60 min)

---

#### Day 46 — Review & documentation
**Daily Time Budget: ~4.5h**

- [ ] Write ADR-009: "Transactional Outbox Pattern" — explain why: ensures at-least-once event delivery without distributed transactions (45 min)
- [ ] Write ADR-010: "Idempotency Keys for Payments" — explain why: payment networks have retries; must not double-charge (30 min)
- [ ] Write `docs/patterns/outbox.md` — explain outbox pattern with sequence diagram in ASCII (1h)
- [ ] Run `ruff`, `mypy`, `pytest` — fix all issues (30–60 min)
- [ ] Update Swagger description for payment endpoints with idempotency key instructions (20 min)

---

### Frontend Tasks
- [ ] Build `AdminOrdersPage` with status filter and pagination (1.5h)
- [ ] Build `OrderDetailPage` with audit log timeline (1h)
- [ ] Show payment status on order confirmation page (30 min)
- [ ] Add cancel button for eligible orders (30 min)

### Database Changes
- [ ] Add `payments` table: id, order_id FK unique, amount, status, gateway_reference (25 min)
- [ ] Add `idempotency_keys` table: id, key unique, user_id FK, response_status_code, response_body JSON, created_at, expires_at (25 min)
- [ ] Add `outbox_events` table: id, aggregate_type, aggregate_id, event_type, payload JSON, published bool default false, retry_count, created_at, published_at (30 min)
- [ ] Add `order_audit_log` table: id, order_id FK, from_status, to_status, changed_by FK, changed_at, note (25 min)
- [ ] Index on `outbox_events (published, created_at)` for relay polling query (15 min)

### DevOps & Infrastructure Tasks
- [ ] No new services; confirm `docker compose up` works (10 min)
- [ ] Ensure outbox relay starts with app (startup event) and stops on shutdown (20 min)

### Testing Tasks
- [ ] `test_valid_order_state_transition` (20 min)
- [ ] `test_invalid_state_transition_rejected` (15 min)
- [ ] `test_payment_success_transitions_order` (30 min)
- [ ] `test_idempotent_payment_no_duplicate` (45 min)
- [ ] `test_outbox_event_created_atomically` (30 min)
- [ ] `test_cancel_returns_stock` (30 min)
- [ ] `test_audit_log_entry_written` (20 min)

### Architecture Improvements
- [ ] ADR-009: Transactional Outbox Pattern
- [ ] ADR-010: Idempotency Keys for Payments
- [ ] Document order state machine transitions in `docs/patterns/order_state_machine.md`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 39 | Order state machine | 5h |
| 40 | Payment model & idempotency keys | 5.5h |
| 41 | Mock payment gateway & payment endpoint | 5h |
| 42 | Outbox pattern implementation | 5.5h |
| 43 | Order cancellation & stock return | 5h |
| 44 | Admin order management dashboard | 5h |
| 45 | Outbox relay hardening & integration test | 5h |
| 46 | Review & documentation | 4.5h |
| **Total** | | **~40.5h** |

### Expected Deliverables
- [ ] Payment endpoint with idempotency key working
- [ ] Order state machine with audit log
- [ ] Outbox table populated on every payment event
- [ ] Order cancellation returns stock
- [ ] Admin order management UI

### Definition of Done
- [ ] Duplicate payment with same idempotency key returns same response, no double-charge
- [ ] Outbox event and payment are in same DB transaction (both succeed or both fail)
- [ ] Invalid state transitions return 422
- [ ] All 7 new tests pass in CI

### Pitfalls to Avoid
- **Never call the payment gateway inside a DB transaction** — external HTTP calls inside a transaction hold the connection open for the full gateway latency. Call gateway first, then open a short transaction to record the result
- Idempotency key must be scoped to user — key "abc" for user A must not shadow key "abc" for user B
- Outbox relay must handle exceptions per-event — one bad event must not block all subsequent events
- Never transition order status directly without going through the state machine

### Interview Readiness
- Explain the Transactional Outbox Pattern — what problem does it solve?
- Why can't you just publish to a message broker in the same code path as a DB write without the outbox?
- What is an idempotency key and how do you implement idempotent payment processing?
- Explain the difference between at-least-once and exactly-once delivery
- What is a state machine and why is it useful for order status management?
- How do you implement compensation (rollback) in a distributed system without 2PC?

---

## Phase 7: Days 47–54 — Caching, Redis & Background Jobs

**Phase objective:** Add Redis cache-aside for product/category endpoints, implement HTTP caching with ETags, rate-limit auth endpoints, set up Celery with RabbitMQ for async tasks, and extract notification logic into a dedicated Notification Service.

---

### Project Architecture

**Architecture style:** Modular monolith with async workers

**What changed from Phase 6:**
- Added: Redis (caching + rate limiting)
- Added: Celery worker service
- Added: RabbitMQ message broker
- Added: Notification Service (FastAPI, separate process)
- Added: ETag-based HTTP caching

**System diagram (end of Phase 7):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON + Bearer token
    ↓
[FastAPI Monolith :8000]
    ├── Rate limiter → [Redis :6379]   (auth endpoints)
    ├── Cache-aside → [Redis :6379]    (product/category reads)
    ├── Outbox relay → RabbitMQ task
    └── All domains
         | SQL async
         ↓
[PostgreSQL :5432]

[Celery Worker]  ← consumes from RabbitMQ
    | AMQP
    ↔ [RabbitMQ :5672]
    |
    ↓ HTTP (internal)
[Notification Service (FastAPI) :8001]
    ├── /notifications/email
    ├── /notifications/push (stub)
    └── channel registry: OrderConfirmation → email template
         | (dev: logs to stdout; prod: SMTP)
         ↓
[PostgreSQL notification_db :5433]  (own DB for notification logs)

[Docker Compose wraps all above]
```

**Data flow — Order Confirmation Email (most complex new operation):**
1. Payment succeeds → outbox event `OrderConfirmed` marked
2. Celery task `send_order_confirmation.delay(order_id)` called by outbox relay
3. RabbitMQ queues the task
4. Celery worker picks up task → calls `NotificationService.send(type=OrderConfirmation, user_id, context)`
5. Notification Service → looks up `OrderConfirmation` in channel registry → finds email template
6. Notification Service → GET /auth/users/{user_id} (internal gRPC stub for now → HTTP call) to get email address
7. Notification Service sends email via SMTP (dev: MailHog, prod: SES)
8. Notification Service logs delivery to `notification_db`
9. Celery task marks success

---

### Business Features
- [ ] Product and category list responses served from Redis cache (cache-aside, TTL=5min)
- [ ] Cache invalidated when product is updated or deleted
- [ ] `ETag` + `Cache-Control` headers on product endpoints; client gets 304 on unchanged
- [ ] Auth login endpoint rate-limited (10 requests/minute per IP)
- [ ] Order confirmation email sent asynchronously after payment success
- [ ] Invoice PDF generated asynchronously and stored in MinIO (stub storage for now)
- [ ] Notification Service handles all outbound communication channels

---

#### Day 47 — Redis setup & cache-aside
**Daily Time Budget: ~5h**

- [ ] Add `redis[asyncio]` (`aioredis`) to dependencies (15 min)
- [ ] Add Redis service to `docker-compose.yml` (redis:7-alpine, port 6379) (15 min)
- [ ] Write `app/core/cache.py` — `CacheService` wrapping `aioredis.Redis`: `get(key)`, `set(key, value, ttl)`, `delete(key)`, `delete_pattern(pattern)` (1h)
- [ ] Add `REDIS_URL` to settings and inject `CacheService` via FastAPI dependency (30 min)
- [ ] Write `get_or_set` wrapper: `async def get_or_set(cache, key, ttl, factory_fn)` (30 min)
- [ ] Update `ProductService.list_products(filters, cursor)` — check cache first, call DB if miss, store in cache with 5min TTL (45 min)
- [ ] Update `ProductService.get_by_id(id)` — cache individual product with key `product:{id}` (30 min)
- [ ] Verify with logs: first request → DB query; second request → no DB query (30 min)

---

#### Day 48 — Cache invalidation
**Daily Time Budget: ~5h**

- [ ] Update `ProductService.update_product` — invalidate `product:{id}` and `products:list:*` pattern after update (45 min)
- [ ] Update `ProductService.delete_product` — same invalidation (20 min)
- [ ] Write `CacheService.delete_pattern(pattern)` using Redis `SCAN` (not `KEYS` — explain why in comment) (1h)
- [ ] Apply same cache-aside to `CategoryService.list_categories` and `CategoryService.get_by_id` (45 min)
- [ ] Write tests: `test_cache_hit_on_second_request` (mock Redis), `test_cache_invalidated_on_update`, `test_cache_invalidated_on_delete` (1.5h)

---

#### Day 49 — ETag + Cache-Control + 304 Not Modified
**Daily Time Budget: ~5h**

- [ ] Write `ETagMiddleware` — computes MD5 of response body, sets `ETag: "<hash>"` and `Cache-Control: public, max-age=300` headers on GET responses (1.5h)
- [ ] Handle `If-None-Match` request header — compare with current ETag; if match, return 304 with empty body (1h)
- [ ] Apply only to product and category GET endpoints (not auth or write endpoints) (30 min)
- [ ] Test with curl: first request → 200 + ETag header; second request with `If-None-Match: <etag>` → 304 (30 min)
- [ ] Write test: `test_304_on_unchanged_product` (30 min)
- [ ] Document ETag flow in `docs/caching/etag.md` (30 min)

---

#### Day 50 — Redis rate limiting on auth endpoints
**Daily Time Budget: ~5h**

- [ ] Write `RateLimiter` using Redis INCR + EXPIRE: `check_rate_limit(ip, key, limit, window_seconds)` → raises `RateLimitExceeded` if over limit (1.5h)
- [ ] Apply `RateLimiter` as FastAPI dependency on `POST /auth/login` and `POST /auth/register` — 10 requests/minute per IP (45 min)
- [ ] Return `429 Too Many Requests` with `Retry-After` header (30 min)
- [ ] Write test: send 11 login requests → 11th returns 429 (30 min)
- [ ] Add `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers to all auth responses (30 min)
- [ ] Document rate limiting strategy (sliding window vs fixed window) in ADR-011 (45 min)

---

#### Day 51 — Celery + RabbitMQ setup
**Daily Time Budget: ~5.5h**

- [ ] Install `celery[rabbitmq]` (15 min)
- [ ] Add RabbitMQ service to `docker-compose.yml` (rabbitmq:3-management, ports 5672, 15672) (15 min)
- [ ] Write `app/worker/celery_app.py` — Celery instance with RabbitMQ broker and Redis result backend (45 min)
- [ ] Add Celery worker service to `docker-compose.yml` — runs `celery -A app.worker.celery_app worker` (20 min)
- [ ] Write first Celery task `send_order_confirmation_email.py` — accepts order_id, logs email body (not real SMTP yet) (45 min)
- [ ] Update outbox relay to call `send_order_confirmation_email.delay(order_id)` when event_type = `OrderConfirmed` (30 min)
- [ ] Verify task appears in RabbitMQ management UI at localhost:15672 (20 min)
- [ ] Write test: `test_celery_task_dispatched_on_order_confirmed` (using `task.apply()` synchronously in test) (1h)
- [ ] Add MailHog service to `docker-compose.yml` (mailhog/mailhog, ports 1025 SMTP, 8025 UI) (15 min)

---

#### Day 52 — Notification Service (FastAPI)
**Daily Time Budget: ~5.5h**

- [ ] Create `notification-service/` directory as a separate Python project (not a subdirectory of app/) (20 min)
- [ ] Scaffold `notification-service/` with `pyproject.toml`, FastAPI app, own `Dockerfile` (45 min)
- [ ] Write `NotificationChannel` Enum: EMAIL, PUSH, SMS (stub) (15 min)
- [ ] Write `NotificationTemplate` registry: maps `(event_type, channel)` → template string (1h)
- [ ] Write `POST /notifications/send` internal endpoint — accepts `{type, user_id, context}`, resolves template, sends via channel (1h)
- [ ] Implement email channel: calls MailHog SMTP (dev) using `aiosmtplib` (1h)
- [ ] Add `notification-service` to `docker-compose.yml` (port 8001) (20 min)
- [ ] Update Celery task to call Notification Service via HTTP instead of sending email directly (30 min)

---

#### Day 53 — Notification Service: own DB + delivery log
**Daily Time Budget: ~5h**

- [ ] Add `notification_db` (separate PostgreSQL) to `docker-compose.yml` (port 5433) (15 min)
- [ ] Write `NotificationLog` SQLAlchemy model: id, event_type, user_id, channel, status (SENT/FAILED), sent_at, error_message (30 min)
- [ ] Run Alembic migration inside `notification-service` (30 min)
- [ ] Write `NotificationLogRepository` — create, get_by_user_id, get_by_event_type (30 min)
- [ ] Update `/notifications/send` to log every attempt and outcome to notification_db (30 min)
- [ ] Write `GET /notifications/logs?user_id=X` — admin endpoint (30 min)
- [ ] Write health + readiness endpoints for Notification Service (20 min)
- [ ] Write framework choice justification (3 bullets): FastAPI for Notification Service because: async SMTP fits async framework; Pydantic for typed event payloads; no ORM ceremony needed beyond simple log table (30 min)
- [ ] Write integration test: order confirmed → outbox → celery → notification-service called → log written (1h)

---

#### Day 54 — Full phase test suite & review
**Daily Time Budget: ~4.5h**

- [ ] Write `test_cache_hit_avoids_db_query` (count DB calls with mock) (30 min)
- [ ] Write `test_rate_limit_triggers_at_11th_request` (30 min)
- [ ] Write `test_304_returned_on_unchanged_resource` (20 min)
- [ ] Write `test_notification_service_health` (10 min)
- [ ] Run full test suite — all must pass (30–60 min)
- [ ] Write ADR-011: Redis rate limiting — sliding window vs token bucket (30 min)
- [ ] Write ADR-012: "Notification Service as dedicated FastAPI service" — explain channel registry pattern (30 min)

---

### Frontend Tasks
- [ ] Display "Email confirmation sent" toast after successful checkout (20 min)
- [ ] No other major frontend work this phase

### Database Changes
- [ ] Add `notification_db` (separate PostgreSQL instance for Notification Service) (15 min)
- [ ] Add `notification_logs` table in notification_db: id, event_type, user_id, channel, status, sent_at, error_message (30 min)

### DevOps & Infrastructure Tasks
- [ ] Add Redis to `docker-compose.yml` with named volume (15 min)
- [ ] Add RabbitMQ to `docker-compose.yml` with management plugin (20 min)
- [ ] Add Celery worker service to `docker-compose.yml` (20 min)
- [ ] Add MailHog service to `docker-compose.yml` (15 min)
- [ ] Add Notification Service (`notification-service/`) to `docker-compose.yml` (20 min)
- [ ] Add `notification_db` PostgreSQL to `docker-compose.yml` (15 min)

### Testing Tasks
- [ ] `test_product_served_from_cache_on_second_request` (30 min)
- [ ] `test_cache_invalidated_on_product_update` (25 min)
- [ ] `test_etag_304_response` (20 min)
- [ ] `test_rate_limit_429_on_11th_login` (25 min)
- [ ] `test_celery_task_enqueued_on_order_confirm` (30 min)
- [ ] `test_notification_service_sends_email` (mock SMTP) (30 min)
- [ ] `test_notification_log_written_on_send` (25 min)

### Architecture Improvements
- [ ] ADR-011: Redis sliding window rate limiting
- [ ] ADR-012: Notification Service — FastAPI + channel registry pattern
- [ ] Document cache key naming convention: `{entity}:{id}` and `{entity}:list:{hash_of_filters}`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 47 | Redis setup & cache-aside | 5h |
| 48 | Cache invalidation | 5h |
| 49 | ETag + Cache-Control + 304 | 5h |
| 50 | Redis rate limiting | 5h |
| 51 | Celery + RabbitMQ setup | 5.5h |
| 52 | Notification Service (FastAPI) | 5.5h |
| 53 | Notification Service: own DB + delivery log | 5h |
| 54 | Full phase test suite & review | 4.5h |
| **Total** | | **~40.5h** |

### Expected Deliverables
- [ ] Redis caching live for product/category read endpoints
- [ ] 304 Not Modified working with ETags
- [ ] Auth endpoints rate-limited (429 after 10/min)
- [ ] Celery + RabbitMQ worker sending email on order confirmation
- [ ] Notification Service running as separate FastAPI service with its own DB

### Definition of Done
- [ ] Cache hit rate visible in Redis INFO (verify second request doesn't query DB)
- [ ] Duplicate login attempts beyond 10/min return 429
- [ ] Email visible in MailHog UI after checkout
- [ ] All 7 new tests pass in CI

### Pitfalls to Avoid
- Use Redis `SCAN` not `KEYS` for pattern-based cache invalidation — `KEYS` blocks the server
- Celery result backend in Redis can grow unboundedly — set `result_expires=3600`
- Do not use `FOR UPDATE` inside a Celery task — tasks run outside the web request transaction
- Rate limiter must use IP from `X-Forwarded-For` behind a proxy, not `request.client.host`
- Do not store sensitive data (JWT tokens, passwords) in Redis without encryption

### Interview Readiness
- Explain cache-aside pattern vs write-through vs write-behind
- How do ETags work and what is 304 Not Modified?
- Explain Redis INCR + EXPIRE for rate limiting — why is this atomic?
- What is Celery and how does it use RabbitMQ?
- Why extract Notification Service vs keeping it in the monolith?
- What is a channel registry pattern in notification systems?

---

## Phase 8: Days 55–63 — Microservices Split (Django Catalog + Django Delivery & Warehouse)

**Phase objective:** Extract catalog (products, categories, attributes, variants, stock) into a Django + DRF catalog-service and extract warehouse/delivery into a Django + DRF delivery-warehouse-service with Django Admin. Auth, Payment, and Notification remain FastAPI. Introduce an API Gateway. Add per-service databases and contract tests.

---

### Project Architecture

**Architecture style:** Partial microservices (catalog and delivery-warehouse extracted)

**What changed from Phase 7:**
- Added: `catalog-service` (Django + DRF + PostgreSQL catalog_db)
- Added: `delivery-warehouse-service` (Django + DRF + PostgreSQL delivery_db + Django Admin)
- Added: `api-gateway` (FastAPI, replaces direct client→monolith calls)
- Added: `.proto` files for gRPC between services
- Replaced: FastAPI catalog routes → Django DRF catalog-service routes (via gateway)
- Auth stays FastAPI. Payment stays FastAPI. Notification stays FastAPI.

**System diagram (end of Phase 8):**
```
[Browser]
    | HTTP :3000
    ↓
[React + TypeScript (Vite)]
    | REST/JSON
    ↓
[API Gateway (FastAPI ASGI) :8080]
    ├── validates JWT → Auth Service (gRPC :50051)
    ├── /catalog/* → Catalog Service (HTTP :8002)
    ├── /orders/*  → Order Service FastAPI (HTTP :8000)
    ├── /payments/* → Payment Service FastAPI (HTTP :8003)
    └── /delivery/* → Delivery & Warehouse Service (HTTP :8004)

[Auth Service (FastAPI ASGI) :50051]
    | SQL
    ↓ [auth_db PostgreSQL :5432]

[Catalog Service (Django/DRF WSGI) :8002]
    | SQL
    ↓ [catalog_db PostgreSQL :5434]

[Delivery & Warehouse Service (Django/DRF WSGI) :8004]
    | Django Admin at /admin/
    | SQL
    ↓ [delivery_db PostgreSQL :5435]

[Order Service (FastAPI ASGI) :8000]
    | SQL
    ↓ [order_db PostgreSQL :5436]

[Payment Service (FastAPI ASGI) :8003]
    | SQL
    ↓ [payment_db PostgreSQL :5437]

[Notification Service (FastAPI ASGI) :8001]
    ↓ [notification_db PostgreSQL :5433]

[Redis :6379]  [RabbitMQ :5672]  [Celery Worker]

[Docker Compose wraps all above]
```

**Data flow — Browse Products (after split):**
1. React → GET /catalog/products → API Gateway
2. Gateway validates JWT → Auth Service (gRPC GetUserByToken)
3. Gateway proxies → Catalog Service (Django DRF) GET /api/products/
4. DRF view → Django ORM → catalog_db (PostgreSQL)
5. JSON response flows back through Gateway → React

---

### Business Features
- [ ] All catalog reads/writes go through Django DRF (same business features as before)
- [ ] Warehouse staff can log in to Django Admin at delivery-warehouse-service/admin/
- [ ] Warehouse staff can update shipment status via Django Admin
- [ ] All services have their own isolated databases (no shared DB)
- [ ] API Gateway validates all JWTs centrally — no service validates tokens itself

---

#### Day 55 — API Gateway (FastAPI) scaffold
**Daily Time Budget: ~5h**

- [ ] Create `api-gateway/` directory with FastAPI app, `pyproject.toml`, `Dockerfile` (30 min)
- [ ] Write `api-gateway/app/main.py` — FastAPI app with reverse-proxy middleware using `httpx.AsyncClient` (1h)
- [ ] Write `ProxyRouter` — generic route that forwards request to downstream service, copies headers and body (1.5h)
- [ ] Add `api-gateway` to `docker-compose.yml` on port 8080 (20 min)
- [ ] Write health endpoint `GET /health` on gateway (10 min)
- [ ] Write `test_gateway_proxies_to_catalog` — mock downstream, verify request forwarded (45 min)
- [ ] Update React `baseURL` to point to gateway :8080 (15 min)

---

#### Day 56 — Django Catalog Service: project setup
**Daily Time Budget: ~5.5h**

- [ ] Create `catalog-service/` directory, initialize with `django-admin startproject catalog_service .` (20 min)
- [ ] Install `django djangorestframework psycopg2-binary django-filter gunicorn django-environ` — note: `django-environ` (package `environ`) is the correct package for settings from env vars; `gunicorn` is used as the WSGI server for Django in production (Docker/K8s), not uvicorn which is ASGI-only (15 min)
- [ ] Create `catalog_service/settings.py` using `environ.Env()` from `django-environ` — DB, allowed hosts, installed apps (45 min)
- [ ] Create `catalog_service/apps/products/models.py` — migrate existing Product, Category, Attribute, AttributeValue, ProductVariant, Stock models to Django ORM (1.5h)
- [ ] Run `python manage.py makemigrations` and `python manage.py migrate` against catalog_db (30 min)
- [ ] Write framework choice justification: Django for catalog because: 1. mature ORM for complex relational data with many joins; 2. `django-filter` for DRF filtering without boilerplate; 3. WSGI is fine — no streaming or WebSocket needed for catalog reads (20 min)
- [ ] Create `catalog-service/Dockerfile` — use `gunicorn catalog_service.wsgi:application --bind 0.0.0.0:8002 --workers 2` as the CMD, not uvicorn (Django is WSGI, not ASGI) (20 min)
- [ ] Add `catalog-service` to `docker-compose.yml` with `catalog_db` (20 min)
- [ ] Add own health endpoint `GET /health/` using DRF `APIView` (15 min)

---

#### Day 57 — Django DRF: serializers, views, routers
**Daily Time Budget: ~5.5h**

- [ ] Write `ProductSerializer`, `CategorySerializer`, `AttributeSerializer`, `ProductVariantSerializer` using `ModelSerializer` (1.5h)
- [ ] Write `ProductViewSet` using `ModelViewSet` — list, retrieve, create, update, destroy (45 min)
- [ ] Write `CategoryViewSet` using `ModelViewSet` (30 min)
- [ ] Register routers: `router = DefaultRouter(); router.register('products', ProductViewSet)` (20 min)
- [ ] Add `django-filter` backend to `ProductViewSet` — filter by `category`, `seller_id`, `is_active`, `min_price`, `max_price` (45 min)
- [ ] Add cursor pagination using DRF `CursorPagination` (30 min)
- [ ] Implement FastAPI vs DRF comparison task: implement the same `GET /categories/` endpoint in both; compare:
  - FastAPI: `router.get()` + `Pydantic schema` + `async def` + `repository.get_all()`
  - DRF: `CategoryViewSet(ModelViewSet)` + `CategorySerializer(ModelSerializer)` + `router.register()`
  - Document in `docs/framework_comparison/fastapi_vs_drf.md` (1.5h)

---

#### Day 58 — Django Catalog: wire into gateway + contract tests
**Daily Time Budget: ~5.5h**

- [ ] Update API Gateway to proxy `/catalog/*` → Catalog Service :8002 (30 min)
- [ ] Test: React → Gateway → DRF → product list returned (end-to-end in browser) (30 min)
- [ ] Write `catalog-service/tests/test_products_api.py` using DRF's `APITestCase` — test CRUD (1.5h)
- [ ] Write contract test `tests/contract/test_gateway_catalog_contract.py` — verify gateway request shape matches DRF expected schema (use Pact or manual JSON schema assertion) (1.5h)
- [ ] Verify JWT auth flows through gateway → DRF endpoint validates `Authorization` header forwarded by gateway (45 min)

---

#### Day 59 — Django Delivery & Warehouse Service: setup
**Daily Time Budget: ~5.5h**

- [ ] Create `delivery-warehouse-service/` directory, initialize Django project (20 min)
- [ ] Install `django djangorestframework psycopg2-binary gunicorn django-environ` (10 min)
- [ ] Write models: `Warehouse` (name, location, capacity, operating_hours JSON), `Shipment` (order_id, carrier, tracking_number, status Enum, created_at), `DeliverySlot` (warehouse FK, start_time, end_time, max_orders) (1.5h)
- [ ] Run `makemigrations` and `migrate` against delivery_db (20 min)
- [ ] Write framework choice justification: Django for delivery-warehouse because: 1. Django Admin panel is a natural fit for warehouse staff (non-technical) to manage shipments without building custom UI; 2. complex relational logistics data fits mature ORM; 3. WSGI acceptable — no streaming needed for warehouse operations (20 min)
- [ ] Create `Dockerfile`, add to `docker-compose.yml` with `delivery_db` :8004 (30 min)
- [ ] Write `GET /health/` and `GET /ready/` endpoints (20 min)
- [ ] Create Django superuser in entrypoint script for admin access (15 min)

---

#### Day 60 — Django Admin for warehouse staff
**Daily Time Budget: ~5h**

- [ ] Register `Warehouse`, `Shipment`, `DeliverySlot` in `admin.py` (30 min)
- [ ] Customize `ShipmentAdmin` — list_display: order_id, carrier, tracking_number, status; list_filter: status; search_fields: tracking_number (45 min)
- [ ] Add `ShipmentAdmin.save_model` override — when status changes to DELIVERED, write to outbox table (stub for now) (45 min)
- [ ] Write `docs/django_admin_rationale.md` — explain why Django Admin fits warehouse staff: out-of-the-box CRUD, permission groups per staff role, no custom UI needed vs building a React admin page (30 min)
- [ ] Access Django Admin at localhost:8004/admin/ — verify warehouse CRUD (30 min)
- [ ] Write DRF `ShipmentViewSet` with `UpdateShipmentStatus` action (for gRPC stub) (1h)
- [ ] Write DRF `DeliverySlotViewSet` (30 min)

---

#### Day 61 — gRPC .proto definitions
**Daily Time Budget: ~5h**

- [ ] Install `grpcio grpcio-tools` in auth-service and gateway (15 min)
- [ ] Write `proto/auth.proto` — service `AuthService { rpc ValidateToken(TokenRequest) returns (UserResponse); rpc GetUserById(UserIdRequest) returns (UserResponse); }` (45 min)
- [ ] Write `proto/catalog.proto` — service `CatalogService { rpc GetProduct(ProductIdRequest) returns (ProductResponse); rpc CheckStock(StockRequest) returns (StockResponse); }` (30 min)
- [ ] Write `proto/delivery.proto` — service `DeliveryService { rpc GetShipmentStatus(ShipmentRequest) returns (ShipmentResponse); rpc UpdateShipmentStatus(UpdateShipmentRequest) returns (ShipmentResponse); }` (30 min)
- [ ] Run `python -m grpc_tools.protoc` to generate Python stubs (30 min)
- [ ] Implement `AuthService.ValidateToken` in auth-service as gRPC handler (1h)
- [ ] Update API Gateway JWT validation to call auth-service via gRPC instead of decoding locally (1h)

---

#### Day 62 — Service isolation: separate databases
**Daily Time Budget: ~5.5h**

- [ ] Create separate PostgreSQL instances in `docker-compose.yml`: auth_db :5432, catalog_db :5434, delivery_db :5435, order_db :5436, payment_db :5437 (45 min)
- [ ] Update each service's settings to point to its own DB (30 min)
- [ ] Write `scripts/verify_isolation.py` — connects to each DB, verifies only expected tables exist, exits non-zero if cross-contamination detected (1h)
- [ ] Run the isolation verifier in CI (30 min)
- [ ] Write `test_no_cross_db_access` — catalog service cannot connect to auth_db (mock connection refusal) (30 min)
- [ ] Update Alembic configs in FastAPI services to point to their own DBs (30 min)
- [ ] Document ADR-013: "Database-per-service" — explain why: independent deployability, schema ownership, prevents coupling (45 min)

---

#### Day 63 — Contract tests for all service boundaries
**Daily Time Budget: ~4.5h**

- [ ] Write contract test: gateway → auth-service (ValidateToken) (30 min)
- [ ] Write contract test: gateway → catalog-service (GET /products/:id) (30 min)
- [ ] Write contract test: gateway → order-service (POST /orders) (30 min)
- [ ] Write contract test: order-service → delivery-warehouse-service (GetShipmentStatus) (30 min)
- [ ] Write `tests/contract/README.md` — explain consumer-driven contract testing approach (30 min)
- [ ] Run all contract tests in CI pipeline (30 min)
- [ ] Phase retrospective: document what changed, what's harder in microservices vs monolith (30 min)

---

### Frontend Tasks
- [ ] Update `src/api/client.ts` — all requests go to gateway :8080 not monolith :8000 (20 min)
- [ ] No functional changes — same UI; verify all pages still work via gateway (30 min)

### Database Changes
- [ ] Separate PostgreSQL instances per service in docker-compose (45 min)
- [ ] Catalog service migrations via Django `manage.py migrate` (30 min)
- [ ] Delivery-warehouse service migrations via Django `manage.py migrate` (20 min)
- [ ] Data migration scripts to seed catalog_db from monolith (1h)

### DevOps & Infrastructure Tasks
- [ ] 6 separate PostgreSQL services in `docker-compose.yml` (45 min)
- [ ] `catalog-service/Dockerfile` (20 min)
- [ ] `delivery-warehouse-service/Dockerfile` (20 min)
- [ ] `api-gateway/Dockerfile` (20 min)
- [ ] Update CI to build and test all services (45 min)

### Testing Tasks
- [ ] DRF `APITestCase` for catalog CRUD (1h)
- [ ] Contract test: gateway → catalog (30 min)
- [ ] Contract test: gateway → auth gRPC (30 min)
- [ ] Contract test: order → delivery (30 min)
- [ ] `test_django_admin_accessible` — verify /admin/ returns 200 with superuser credentials (20 min)
- [ ] `test_shipment_status_update_via_admin` (30 min)
- [ ] `test_db_isolation` — catalog service tables not in auth_db (30 min)

### Architecture Improvements
- [ ] ADR-013: Database-per-service isolation
- [ ] ADR-014: API Gateway as single entry point (JWT validation centralized)
- [ ] Document FastAPI vs Django comparison in `docs/framework_comparison/fastapi_vs_drf.md`
- [ ] Document Django Admin rationale for warehouse staff in `docs/django_admin_rationale.md`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 55 | API Gateway (FastAPI) scaffold | 5h |
| 56 | Django Catalog Service: project setup | 5.5h |
| 57 | Django DRF: serializers, views, routers | 5.5h |
| 58 | Catalog: wire into gateway + contract tests | 5.5h |
| 59 | Django Delivery & Warehouse: setup | 5.5h |
| 60 | Django Admin for warehouse staff | 5h |
| 61 | gRPC .proto definitions | 5h |
| 62 | Service isolation: separate databases | 5.5h |
| 63 | Contract tests for all service boundaries | 4.5h |
| **Total** | | **~46.5h** |

### Expected Deliverables
- [ ] API Gateway running at :8080, all routes proxied correctly
- [ ] Catalog Service (Django DRF) running at :8002 with full CRUD
- [ ] Delivery & Warehouse Service (Django DRF) running at :8004
- [ ] Django Admin accessible at :8004/admin/ with shipment management
- [ ] gRPC stubs for auth and catalog
- [ ] 7 contract tests passing
- [ ] Each service has its own PostgreSQL database

### Definition of Done
- [ ] `docker compose up` starts all 8 services + 6 databases
- [ ] React app works end-to-end through the API Gateway
- [ ] Django Admin panel accessible and functional for warehouse staff
- [ ] All contract tests pass in CI
- [ ] No service can connect to another service's database (isolation verified)

### Pitfalls to Avoid
- Django ORM is synchronous (WSGI) — do NOT mix asyncio with Django ORM outside `sync_to_async` wrappers
- DRF `ModelSerializer` exposes all fields by default — always specify `fields = [...]` explicitly to avoid accidental data leaks
- Django Admin requires `python manage.py createsuperuser` — automate this in entrypoint for dev
- gRPC server must run in a separate thread or process from the Django WSGI server
- Contract tests must be run in CI against real service instances, not mocks — otherwise they test nothing

### Interview Readiness
- Compare Django ORM vs SQLAlchemy — when would you choose each?
- Compare DRF `ModelSerializer` vs Pydantic model — what are the tradeoffs?
- Compare DRF `ViewSet` vs FastAPI router — routing, middleware, dependency injection
- Why does Django not support async out of the box and what is the `sync_to_async` solution?
- What is gRPC and why use it for inter-service communication instead of REST?
- What is consumer-driven contract testing and how does it differ from integration testing?
- Why use Django Admin for warehouse staff UI instead of building a React frontend?

---

## Phase 9: Days 64–71 — Event-Driven Architecture, Kafka & Product Activity Monitor

**Phase objective:** Replace the outbox relay stub with real Kafka producers/consumers, implement a Saga orchestrator for the checkout→payment→shipment flow, add CQRS read models, wire live order updates via SSE, and introduce the Product Activity Monitor as a lightweight Flask service backed by MongoDB.

---

### Project Architecture

**Architecture style:** Full microservices with event-driven core

**What changed from Phase 8:**
- Added: Kafka (3-node dev cluster via Docker)
- Added: Saga orchestrator in Order Service
- Added: `Product Activity Monitor` (Flask + MongoDB)
- Added: Kafka consumers in Notification Service and Delivery-Warehouse Service
- Added: SSE endpoint for live order status updates
- Added: CQRS `order_summaries` read model
- Replaced: outbox relay stub with real Kafka publisher

**System diagram (end of Phase 9):**
```
[Browser]
    | HTTP :3000 + SSE /orders/{id}/stream
    ↓
[React + TypeScript]
    | REST/JSON
    ↓
[API Gateway (FastAPI ASGI) :8080]
    ├── Auth Service (FastAPI) ←gRPC→ [auth_db]
    ├── Catalog Service (Django/DRF WSGI) ←SQL→ [catalog_db]
    ├── Order Service (FastAPI ASGI) ←SQL→ [order_db]
    │     └── Saga Orchestrator
    ├── Payment Service (FastAPI ASGI) ←SQL→ [payment_db]
    └── Delivery & Warehouse (Django/DRF WSGI) ←SQL→ [delivery_db]
          └── Django Admin

[Kafka :9092]
    Topics:
    ├── orders.created      → Saga Orchestrator
    ├── inventory.reserved  → Saga Orchestrator
    ├── payments.succeeded  → Delivery Service, Notification Service
    ├── payments.failed     → Saga Orchestrator (compensate)
    ├── shipments.created   → Notification Service
    ├── shipments.delivered → Notification Service
    ├── catalog.product.*   → Product Activity Monitor
    └── orders.saga.state   → CQRS read model

[Notification Service (FastAPI)] ← Kafka consumer → sends email/push
[Product Activity Monitor (Flask) :8005] ← Kafka consumer
    └── [MongoDB :27017] (audit log)

[Redis :6379]  [RabbitMQ :5672]  [Celery Worker]

[Docker Compose wraps all above]
```

**Data flow — Saga: Order → Payment → Shipment:**
1. Customer → POST /checkout → Order Service
2. Order Service creates order (PENDING) → publishes `orders.created` to Kafka
3. Saga Orchestrator consumes `orders.created` → calls Inventory Service: reserve stock
4. Inventory publishes `inventory.reserved` → Saga Orchestrator
5. Saga Orchestrator calls Payment Service: charge
6. Payment Service publishes `payments.succeeded` → Kafka
7. Delivery-Warehouse Service consumes `payments.succeeded` → auto-creates Shipment → publishes `shipments.created`
8. Notification Service consumes `payments.succeeded` → sends "Payment confirmed" email
9. Notification Service consumes `shipments.created` → sends "Shipment dispatched" email
10. On `payments.failed` → Saga Orchestrator publishes compensation: `inventory.release` → Inventory releases stock → Order marked CANCELLED

---

### Business Features
- [ ] Real-time order status updates pushed to browser via SSE
- [ ] Saga ensures payment failure triggers stock release automatically
- [ ] Shipment auto-created on payment success (no manual warehouse step)
- [ ] Product Activity Monitor logs every ProductCreated/Updated/Deleted event
- [ ] Internal admins can query activity log by product_id, user_id, or date range
- [ ] Notification Service is fully event-driven (no direct service calls)

---

#### Day 64 — Kafka setup
**Daily Time Budget: ~5h**

- [ ] Add Kafka (confluentinc/cp-kafka) + Zookeeper to `docker-compose.yml` (or use Redpanda for simpler setup) (45 min)
- [ ] Install `aiokafka` in Order Service and other producers (15 min)
- [ ] Write `app/kafka/producer.py` — `KafkaProducerClient.publish(topic, key, payload)` with JSON serialization (1h)
- [ ] Write `app/kafka/consumer.py` — base `KafkaConsumer` class with `consume(topic, group_id, handler_fn)` loop (1h)
- [ ] Update outbox relay in Order Service: instead of logging to stdout, publish to Kafka topic (1h)
- [ ] Verify message in Kafka using `kafka-console-consumer` (20 min)
- [ ] Write test: `test_kafka_producer_publishes_on_order_created` (mock aiokafka) (30 min)

---

#### Day 65 — Saga orchestrator
**Daily Time Budget: ~5.5h**

- [ ] Write `app/domains/orders/saga/orchestrator.py` — `CheckoutSaga` class that tracks state: `STARTED → INVENTORY_RESERVED → PAYMENT_PROCESSING → PAYMENT_SUCCESS/FAILED → COMPLETED/COMPENSATING` (1.5h)
- [ ] Write `SagaState` model: id, order_id FK (unique), state (Enum), created_at, updated_at (30 min)
- [ ] Generate migration for saga_states table (15 min)
- [ ] Implement saga step handlers as Kafka consumers on order_service: `on_inventory_reserved`, `on_payment_succeeded`, `on_payment_failed` (2h)
- [ ] Implement compensation: `on_payment_failed` → publish `inventory.release` → update order to CANCELLED (45 min)
- [ ] Write test: `test_saga_compensates_on_payment_failure` (30 min)

---

#### Day 66 — Delivery-Warehouse: Kafka consumer
**Daily Time Budget: ~5h**

- [ ] Add `kafka-python` or `aiokafka` to delivery-warehouse-service (note: Django is WSGI, so use threading-based Kafka consumer or run as separate management command) (30 min)
- [ ] Write Django management command `handle_kafka_events.py` — runs `aiokafka` consumer in `asyncio.run()` listening to `payments.succeeded` (1.5h)
- [ ] On `payments.succeeded` event: auto-create `Shipment` record (order_id, status=PENDING, carrier=unassigned) → save to delivery_db (45 min)
- [ ] Publish `shipments.created` event to Kafka after shipment created (30 min)
- [ ] Add management command to `docker-compose.yml` as a separate service: `delivery-kafka-consumer` (20 min)
- [ ] Write test: `test_shipment_created_on_payment_succeeded_event` (45 min)

---

#### Day 67 — Notification Service: fully event-driven
**Daily Time Budget: ~5h**

- [ ] Replace Celery task call in outbox relay with Kafka publication (30 min)
- [ ] Write Kafka consumers in Notification Service for topics: `payments.succeeded`, `shipments.created`, `shipments.delivered` (1.5h)
- [ ] Map each event type to a notification: `payments.succeeded` → OrderConfirmed email; `shipments.created` → ShipmentDispatched email; `shipments.delivered` → DeliveredConfirmation email (45 min)
- [ ] Remove direct HTTP call from Celery to Notification Service — Notification Service now purely event-driven (20 min)
- [ ] Write test: `test_notification_sent_on_payment_succeeded_event` (30 min)
- [ ] Test end-to-end: checkout → kafka → notification → email in MailHog (30 min)
- [ ] Document ADR-015: "Notification Service decoupled via Kafka" — reason: adding new notification types requires no changes to other services (30 min)

---

#### Day 68 — CQRS read model: order_summaries
**Daily Time Budget: ~5h**

- [ ] Write `order_summaries` table in order_db: order_id PK, user_id, status, total, item_count, last_updated (30 min)
- [ ] Write Kafka consumer that listens to `orders.saga.state` topic and upserts into `order_summaries` (1.5h)
- [ ] Write `GET /orders/summaries?user_id=X` endpoint that reads ONLY from `order_summaries` (not joining orders + order_items) (45 min)
- [ ] Document ADR-016: "CQRS read model for order list" — reads from denormalized table, writes go to normalized orders table (30 min)
- [ ] Write test: `test_order_summary_updated_on_saga_state_change` (30 min)
- [ ] Benchmark: compare `GET /orders` (normalized join) vs `GET /orders/summaries` (denormalized) with 10k orders (1h)

---

#### Day 69 — SSE for live order status updates
**Daily Time Budget: ~5h**

- [ ] Write `GET /orders/{id}/stream` FastAPI endpoint using `StreamingResponse` with `EventSourceResponse` pattern (produces `text/event-stream`) (1.5h)
- [ ] When saga state changes → publish to `order:{id}:status` Redis pub/sub channel (30 min)
- [ ] SSE handler subscribes to Redis pub/sub for `order:{id}:status` → streams events to browser (1h)
- [ ] React: add `EventSource` hook in `OrderDetailPage.tsx` that updates status in real time (45 min)
- [ ] Test: checkout in one tab → watch status update live in OrderDetailPage without refresh (30 min)
- [ ] Write test: `test_sse_endpoint_streams_status_updates` (30 min)

---

#### Day 70 — Product Activity Monitor (Flask + MongoDB)
**Daily Time Budget: ~5.5h**

- [ ] Create `product-activity-monitor/` Flask service directory (20 min)
- [ ] Install `flask flask-pymongo kafka-python pymongo` (15 min)
- [ ] Write Flask app in `product-activity-monitor/app.py` — minimal, no ORM (30 min)
- [ ] Write Kafka consumer thread listening to `catalog.product.created`, `catalog.product.updated`, `catalog.product.deleted` (1h)
- [ ] On each event: insert MongoDB document `{product_id, user_id, action, timestamp, before, after}` (30 min)
- [ ] Write `GET /activity?product_id=X` Flask route — queries MongoDB (45 min)
- [ ] Write `GET /activity?user_id=Y` and `GET /activity?date_from=...&date_to=...` (30 min)
- [ ] Write `Dockerfile` for product-activity-monitor (15 min)
- [ ] Add MongoDB `:27017` and `product-activity-monitor :8005` to `docker-compose.yml` (20 min)
- [ ] Write framework choice justification: Flask because: 1. read-only internal tool; 2. no complex ORM needed — pymongo directly; 3. minimal boilerplate vs FastAPI or Django for a tool this simple (20 min)
- [ ] Write MongoDB rationale: append-only audit log fits document store; no joins needed; flexible `before/after` field payloads vary per event type; time-series query by date range is natural in MongoDB (20 min)

---

#### Day 71 — Full Kafka integration tests & review
**Daily Time Budget: ~4.5h**

- [ ] Write `test_saga_happy_path` — mock Kafka, simulate full saga: order → inventory → payment → shipment (1h)
- [ ] Write `test_saga_compensation` — simulate payment failure → stock released → order cancelled (45 min)
- [ ] Write `test_product_activity_logged_on_create` (30 min)
- [ ] Write `test_product_activity_logged_on_delete` (20 min)
- [ ] Run full test suite (30–60 min)
- [ ] Write ADR-017: "Saga Pattern for distributed checkout" — why saga over 2PC (30 min)

---

### Frontend Tasks
- [ ] Add `EventSource` hook in `OrderDetailPage.tsx` for SSE (45 min)
- [ ] Display real-time status update with animated indicator (30 min)
- [ ] Show "Shipment dispatched" notification toast when SSE event arrives (20 min)

### Database Changes
- [ ] Add `saga_states` table to order_db (20 min)
- [ ] Add `order_summaries` table to order_db (20 min)
- [ ] MongoDB collection `product_activity` (schema-less, no migration needed) (10 min)

### DevOps & Infrastructure Tasks
- [ ] Add Kafka + Zookeeper (or Redpanda) to `docker-compose.yml` (45 min)
- [ ] Add MongoDB to `docker-compose.yml` (15 min)
- [ ] Add `product-activity-monitor` service to `docker-compose.yml` (20 min)
- [ ] Add `delivery-kafka-consumer` service to `docker-compose.yml` (15 min)

### Testing Tasks
- [ ] `test_kafka_message_published_on_order_created` (30 min)
- [ ] `test_saga_compensation_releases_stock` (45 min)
- [ ] `test_shipment_created_on_payment_kafka_event` (30 min)
- [ ] `test_notification_triggered_by_kafka_event` (30 min)
- [ ] `test_sse_streams_status_update` (30 min)
- [ ] `test_product_activity_logged` (20 min)
- [ ] `test_cqrs_order_summary_updated` (25 min)

### Architecture Improvements
- [ ] ADR-015: Notification Service decoupled via Kafka
- [ ] ADR-016: CQRS read model for order summaries
- [ ] ADR-017: Saga Pattern for distributed checkout
- [ ] Document Kafka topic naming convention: `{domain}.{entity}.{event}` (e.g., `orders.order.created`)

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 64 | Kafka setup | 5h |
| 65 | Saga orchestrator | 5.5h |
| 66 | Delivery-Warehouse Kafka consumer | 5h |
| 67 | Notification Service: fully event-driven | 5h |
| 68 | CQRS read model: order_summaries | 5h |
| 69 | SSE for live order status | 5h |
| 70 | Product Activity Monitor (Flask + MongoDB) | 5.5h |
| 71 | Full Kafka integration tests & review | 4.5h |
| **Total** | | **~40.5h** |

### Expected Deliverables
- [ ] Kafka topics live; outbox relay publishes real Kafka events
- [ ] Saga orchestrator handles payment failure with stock compensation
- [ ] Product Activity Monitor Flask service with MongoDB audit log
- [ ] SSE streaming live order status updates to browser
- [ ] 7 new tests passing

### Definition of Done
- [ ] End-to-end checkout → Kafka → shipment → notification works
- [ ] Payment failure triggers stock release and order cancellation
- [ ] Product create/update/delete events appear in MongoDB activity log
- [ ] Browser shows live status update without polling

### Pitfalls to Avoid
- Django WSGI cannot run `asyncio` event loop in main thread — run Kafka consumer in a separate thread or management command
- Saga orchestrator must be idempotent — messages can be delivered more than once (at-least-once Kafka)
- MongoDB documents have no schema enforcement — validate in application code before insert
- SSE connections consume a server thread/connection indefinitely — use background task, not blocking call

### Interview Readiness
- Explain the Saga pattern — orchestration vs choreography
- What is CQRS and when does it make sense?
- Explain at-least-once delivery in Kafka — how do you make consumers idempotent?
- Why use MongoDB for an audit log instead of PostgreSQL?
- What is SSE and how does it differ from WebSockets?
- Compare Flask vs FastAPI vs Django for the Product Activity Monitor use case

---

## Phase 10: Days 72–79 — Search, Reviews & Polyglot Persistence

**Phase objective:** Add Elasticsearch for full-text product search with faceted filtering, MongoDB for product reviews, MinIO for product image uploads, and a nightly collaborative filtering recommendations job.

---

### Project Architecture

**Architecture style:** Full microservices with event-driven core + polyglot persistence

**What changed from Phase 9:**
- Added: Elasticsearch (product search index)
- Added: MongoDB reviews collection
- Added: MinIO (S3-compatible object storage for images)
- Added: Celery nightly recommendation job
- Added: Catalog Service publishes to Elasticsearch on product create/update

**System diagram (end of Phase 10):**
```
[Browser]
    | HTTP + SSE
    ↓
[API Gateway (FastAPI) :8080]
    ├── /search/* → Catalog Service (search endpoint via Elasticsearch)
    ├── /reviews/* → Review Service (FastAPI) → [MongoDB :27017]
    ├── /products/*/images → Catalog Service → [MinIO :9000]
    └── ... all other services as Phase 9 ...

[Elasticsearch :9200]  ← indexed by Catalog Service on product events

[Celery Worker] → nightly recommendation job → [recommendation_db PostgreSQL]

[MinIO :9000]  (S3-compatible, product images)

[MongoDB :27017]
    ├── product_activity (Phase 9)
    └── reviews (Phase 10)

All other services, Kafka, Redis, RabbitMQ from Phase 9 unchanged
```

**Data flow — Product Search with Facets:**
1. React → GET /search?q=blue+shirt&category=clothing&min_price=20&max_price=100&page=1
2. Gateway → Catalog Service GET /api/search/
3. DRF search view → Elasticsearch Python client
4. Elasticsearch query: `multi_match` on name/description + `term` filters on category_id, is_active + `range` filter on price
5. Returns hits with `_score`, facet aggregations (count per category, count per price bucket)
6. DRF serializes → JSON with `hits`, `total`, `facets`, `page`

---

### Business Features
- [ ] Users can search products by keyword (full-text across name and description)
- [ ] Search results can be filtered by category, price range, in-stock only
- [ ] Search returns facet counts (e.g., "Clothing (23), Electronics (7)")
- [ ] Users can write, edit, and delete reviews with star rating
- [ ] Users can reply to reviews (nested replies)
- [ ] Product images can be uploaded and served via MinIO
- [ ] Nightly recommendations job suggests products based on purchase history

---

#### Day 72 — Elasticsearch setup & product indexing
**Daily Time Budget: ~5h**

- [ ] Add Elasticsearch (elasticsearch:8.x) to `docker-compose.yml` port 9200 (20 min)
- [ ] Install `elasticsearch[async]` Python client in catalog-service (15 min)
- [ ] Write `catalog_service/search/index.py` — `ProductIndex`: defines index mapping with `name` (text, analyzer=english), `description` (text), `price` (float), `category_id` (keyword), `is_active` (boolean), `sku` (keyword) (1h)
- [ ] Write `create_index()` function — creates index with mapping if not exists (30 min)
- [ ] Write `index_product(product)` — indexes a single product document (30 min)
- [ ] Write Django signal: `post_save` on `Product` model → call `index_product` (45 min)
- [ ] Write Django signal: `post_delete` on `Product` → delete from Elasticsearch index (20 min)
- [ ] Write management command `reindex_all_products` — bulk indexes all existing products (45 min)
- [ ] Run `reindex_all_products`, verify in Elasticsearch with `GET /products/_search?q=*` (20 min)

---

#### Day 73 — Full-text search + faceted filtering endpoint
**Daily Time Budget: ~5h**

- [ ] Write `SearchView` (DRF `APIView`) — accepts `q`, `category_id`, `min_price`, `max_price`, `in_stock`, `page`, `limit` (30 min)
- [ ] Build Elasticsearch query: `bool` query with `must: multi_match(q, fields=[name^3, description])`, `filter: [term(category_id), range(price), term(is_active)]` (1.5h)
- [ ] Add `aggs`: `categories` (terms on category_id), `price_ranges` (range buckets: 0-50, 50-200, 200+) (1h)
- [ ] Serialize Elasticsearch response to `SearchResult` Pydantic schema: hits, total, facets (45 min)
- [ ] Register route `GET /api/search/` in catalog-service URL config (15 min)
- [ ] Wire gateway → catalog-service search (20 min)
- [ ] Test in browser: search "shirt" → results with facets (30 min)

---

#### Day 74 — MongoDB reviews service
**Daily Time Budget: ~5.5h**

- [ ] Create `review-service/` — FastAPI app (or add reviews domain to catalog-service — choose: separate service, document reasoning) (30 min)
- [ ] Install `motor` (async MongoDB driver) (10 min)
- [ ] Write `ReviewRepository` using Motor: `create_review`, `get_by_product_id`, `get_by_user_id`, `update_review`, `delete_review`, `add_reply` (1.5h)
- [ ] Write `Review` document schema: `product_id`, `user_id`, `rating` (1-5), `title`, `body`, `replies` (embedded array), `created_at`, `helpful_count` (30 min)
- [ ] Write FastAPI endpoints: `POST /reviews`, `GET /reviews?product_id=X`, `PUT /reviews/{id}`, `DELETE /reviews/{id}`, `POST /reviews/{id}/replies` (1.5h)
- [ ] Document MongoDB rationale: reviews are append-heavy, replies are naturally embedded sub-documents, no complex joins needed, flexible schema allows varying review metadata per product category (30 min)
- [ ] Write test: `test_create_review`, `test_get_reviews_by_product`, `test_add_reply_to_review` (1h)

---

#### Day 75 — MinIO image uploads
**Daily Time Budget: ~5h**

- [ ] Add MinIO to `docker-compose.yml` (minio/minio, ports 9000 API, 9001 console) (20 min)
- [ ] Install `aiobotocore` or `minio` Python client (15 min)
- [ ] Write `StorageService` — `upload_image(file, product_id)` → uploads to MinIO bucket `product-images`, returns public URL (1.5h)
- [ ] Write `POST /catalog/products/{id}/images` endpoint — accepts `multipart/form-data`, validates file type (JPEG/PNG/WEBP) and size (max 5MB), uploads to MinIO, saves URL to product.image_urls JSON field (1.5h)
- [ ] Write `GET /catalog/products/{id}/images` — returns list of image URLs (20 min)
- [ ] Test image upload via curl with `multipart/form-data` (30 min)
- [ ] Write test: `test_image_upload_success`, `test_image_upload_invalid_type` → 422 (30 min)

---

#### Day 76 — Search tests & React search UI
**Daily Time Budget: ~5h**

- [ ] Write `test_search_returns_relevant_results` — index 10 products, search "blue shirt", verify top hit (45 min)
- [ ] Write `test_search_facets_correct_counts` — verify facet aggregation counts match indexed data (30 min)
- [ ] Write `test_search_price_filter` — results within price range only (25 min)
- [ ] Build `SearchPage.tsx` in React — search input, results list, facet sidebar with checkboxes (1.5h)
- [ ] Add search to navbar — type and redirect to `/search?q=...` (30 min)
- [ ] Display facets with counts, click to add filter (1h)

---

#### Day 77 — React reviews UI
**Daily Time Budget: ~5h**

- [ ] Build `ReviewsList.tsx` — fetch and display reviews for a product, star rating display (1h)
- [ ] Build `ReviewForm.tsx` — star rating picker, title, body fields; submit with `useMutation` (1h)
- [ ] Show average rating on product detail page (30 min)
- [ ] Build `ReplyForm.tsx` — inline reply under each review (45 min)
- [ ] Integrate reviews into `ProductDetailPage.tsx` (30 min)
- [ ] Test: write review → appears in list immediately via React Query invalidation (30 min)

---

#### Day 78 — Collaborative filtering recommendations
**Daily Time Budget: ~5h**

- [ ] Write `celery_tasks/nightly_recommendations.py` — Celery beat task scheduled for 02:00 UTC (15 min)
- [ ] Algorithm: item-based collaborative filtering — for each product, find users who bought it, find other products those users bought, rank by co-purchase frequency (1.5h)
- [ ] Write results to `product_recommendations` table: `product_id`, `recommended_product_id`, `score`, `updated_at` (30 min)
- [ ] Generate migration for `product_recommendations` (15 min)
- [ ] Write `GET /catalog/products/{id}/recommendations` endpoint — reads from recommendations table (30 min)
- [ ] Add Celery beat service to `docker-compose.yml` (20 min)
- [ ] Write test: `test_recommendations_generated_for_co_purchased_products` (45 min)
- [ ] Display 4 recommendation tiles on product detail page in React (1h)

---

#### Day 79 — Phase review & integration tests
**Daily Time Budget: ~4.5h**

- [ ] Write `test_full_search_flow` — create products → index → search → verify results (45 min)
- [ ] Write `test_image_uploaded_served_via_minio` (30 min)
- [ ] Run full test suite (30–60 min)
- [ ] Write ADR-018: "Elasticsearch for product search" — why not PostgreSQL full-text search (30 min)
- [ ] Write ADR-019: "MongoDB for reviews" — document rationale (20 min)
- [ ] Update `README.md` with new services (15 min)

---

### Frontend Tasks
- [ ] `SearchPage.tsx` with facet sidebar and results (1.5h)
- [ ] `ReviewsList.tsx` and `ReviewForm.tsx` (1.5h)
- [ ] Product image gallery on product detail page (45 min)
- [ ] Recommendation tiles on product detail page (45 min)
- [ ] Search bar in navbar (30 min)

### Database Changes
- [ ] Elasticsearch product index with mapping (1h)
- [ ] MongoDB `reviews` collection (no migration — schema-less) (15 min)
- [ ] Add `image_urls` JSON column to `products` in catalog-service (20 min)
- [ ] Add `product_recommendations` table in catalog_db (20 min)

### DevOps & Infrastructure Tasks
- [ ] Add Elasticsearch :9200 to `docker-compose.yml` (20 min)
- [ ] Add MinIO :9000/:9001 to `docker-compose.yml` (20 min)
- [ ] Add Celery beat scheduler to `docker-compose.yml` (15 min)
- [ ] Create MinIO bucket `product-images` in entrypoint (20 min)

### Testing Tasks
- [ ] `test_product_indexed_on_create` (20 min)
- [ ] `test_search_returns_correct_results` (30 min)
- [ ] `test_search_facets_correct` (25 min)
- [ ] `test_review_create_and_retrieve` (25 min)
- [ ] `test_reply_embedded_in_review` (20 min)
- [ ] `test_image_upload_and_url_returned` (25 min)
- [ ] `test_recommendations_generated` (30 min)

### Architecture Improvements
- [ ] ADR-018: Elasticsearch for product search over PostgreSQL FTS
- [ ] ADR-019: MongoDB for reviews (embedded replies, schema flexibility)
- [ ] Document MinIO bucket policy and file naming convention

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 72 | Elasticsearch setup & product indexing | 5h |
| 73 | Full-text search + faceted filtering | 5h |
| 74 | MongoDB reviews service | 5.5h |
| 75 | MinIO image uploads | 5h |
| 76 | Search tests & React search UI | 5h |
| 77 | React reviews UI | 5h |
| 78 | Collaborative filtering recommendations | 5h |
| 79 | Phase review & integration tests | 4.5h |
| **Total** | | **~40h** |

### Expected Deliverables
- [ ] Full-text product search with facets via Elasticsearch
- [ ] Reviews with nested replies stored in MongoDB
- [ ] Product images uploadable to MinIO
- [ ] Nightly recommendation job running in Celery beat
- [ ] 7 new tests passing

### Definition of Done
- [ ] Search "blue shirt" returns relevant results with facet counts
- [ ] Uploading a JPEG to MinIO returns a public URL that loads in browser
- [ ] Review written via UI appears in product page without page reload
- [ ] All tests pass in CI

### Pitfalls to Avoid
- Elasticsearch `multi_match` across unanalyzed keyword fields will not do fuzzy matching — ensure text fields use english analyzer
- MongoDB `ObjectId` is not JSON serializable by default — convert to string in response serialization
- MinIO `presigned_url` expires — do not store presigned URLs; store bucket path and generate URL on-demand
- Celery beat requires only one running instance — do not scale beat horizontally

### Interview Readiness
- How does Elasticsearch inverted index work?
- What is a faceted search and how do you implement it with aggregations?
- When would you choose MongoDB over PostgreSQL for a new feature?
- What is the difference between `motor` (async) and `pymongo` (sync)?
- What is collaborative filtering and how does it differ from content-based filtering?
- How do you handle file uploads in an async web framework (FastAPI)?

---

## Phase 11: Days 80–86 — CI/CD, Multi-Stage Docker & IaC

**Phase objective:** Build a production-quality CI/CD pipeline with GitHub Actions, convert all Dockerfiles to multi-stage builds, enforce semantic versioning, and provision infrastructure with Terraform (or LocalStack).

---

### Project Architecture

**Architecture style:** Full microservices — now with production CI/CD

**What changed from Phase 10:**
- Added: GitHub Actions multi-job CI pipelines per service
- Added: Multi-stage Dockerfiles (all services)
- Added: Image scanning (Trivy)
- Added: Terraform IaC for managed PostgreSQL + container registry
- Added: Semantic versioning via conventional commits
- No new runtime services

**System diagram (end of Phase 11):**
```
[GitHub Repo]
    | push / pull_request
    ↓
[GitHub Actions CI]
    ├── lint (ruff, eslint)
    ├── type-check (mypy, tsc)
    ├── test (pytest, jest) + coverage gate ≥80%
    ├── docker build (multi-stage)
    ├── image scan (Trivy — fail on CRITICAL CVEs)
    └── push to [GitHub Container Registry (GHCR)]

[LocalStack / Terraform] ← provisions:
    ├── RDS PostgreSQL instances (per service)
    └── ECR-equivalent registry

All runtime services same as Phase 10
```

**Data flow — CI push to main:**
1. Developer pushes commit with conventional commit message (`feat:`, `fix:`)
2. GitHub Actions triggers CI workflow
3. Matrix strategy: run lint + type-check + test jobs in parallel per service
4. Coverage gate: pytest-cov must show ≥80% for each service
5. Docker build multi-stage — build image, measure size (must be < 200MB)
6. Trivy scans image — fail if CRITICAL CVEs found
7. On success: tag image with `git describe --tags` (semver), push to GHCR
8. Semantic-release computes next version from commit messages, creates GitHub Release

---

### Business Features
- [ ] Every push to main triggers full test suite + image build automatically
- [ ] PRs blocked if tests fail or coverage drops below 80%
- [ ] Docker images automatically tagged with semantic version on release
- [ ] Images scanned for CVEs before push to registry

---

#### Day 80 — Multi-stage Dockerfiles
**Daily Time Budget: ~5h**

- [ ] Rewrite FastAPI services Dockerfiles as multi-stage: `builder` stage (install deps, compile) + `runtime` stage (copy only site-packages and app code, no build tools) (1.5h)
- [ ] Rewrite Django services Dockerfiles as multi-stage (same pattern) (1h)
- [ ] Rewrite Flask Dockerfile (product-activity-monitor) as multi-stage (30 min)
- [ ] Measure image sizes before and after: run `docker images | grep <service>` and document in `docs/docker/image_sizes.md` (30 min)
- [ ] Verify all services still start correctly after multi-stage conversion (30 min)
- [ ] Add `.dockerignore` files for all services (exclude `.git`, `tests/`, `*.md`, `__pycache__`) (30 min)
- [ ] Target: all Python service images < 200MB (30 min)

---

#### Day 81 — GitHub Actions: CI per service
**Daily Time Budget: ~5.5h**

- [ ] Write `.github/workflows/ci-api-gateway.yml` — on push/PR: checkout, set up Python 3.12, install deps, ruff check, mypy, pytest with coverage, upload coverage to codecov (1h)
- [ ] Write similar workflows for: auth-service, order-service, payment-service, catalog-service (Django), delivery-warehouse-service (Django), notification-service, product-activity-monitor (Flask) — use matrix strategy to DRY (2h)
- [ ] Add `pytest --cov --cov-report=xml --cov-fail-under=80` — CI fails if coverage < 80% (30 min)
- [ ] Add `ruff check` and `mypy --strict` steps — fail on any error (30 min)
- [ ] Write `frontend` CI job: `npm ci`, `tsc --noEmit`, `npm test -- --watchAll=false` (30 min)
- [ ] Push to GitHub — confirm all jobs green on a clean run (30–60 min)

---

#### Day 82 — Docker build + image scan in CI
**Daily Time Budget: ~5h**

- [ ] Add Docker build step to each CI workflow: `docker build -f Dockerfile -t <service>:${{ github.sha }} .` (30 min)
- [ ] Add Trivy scan step: `aquasecurity/trivy-action@master` — scan built image, fail on CRITICAL (45 min)
- [ ] Add image push step (only on `main` branch): push to GHCR with `github.sha` tag (30 min)
- [ ] Fix any CVEs found by Trivy in base images — switch to newer base image versions if needed (30–90 min)
- [ ] Add `docker-compose.ci.yml` — uses built images from GHCR instead of building locally (45 min)
- [ ] Run integration tests in CI using `docker-compose.ci.yml` (45 min)

---

#### Day 83 — Semantic versioning & GitHub Releases
**Daily Time Budget: ~5h**

- [ ] Install `python-semantic-release` or `semantic-release` (Node.js) in repo root (20 min)
- [ ] Write `.releaserc.yml` — configure: analyze commits with conventional commits preset, generate CHANGELOG.md, create GitHub Release, tag image with computed semver (1h)
- [ ] Write commit message convention: `feat:` = minor bump, `fix:` = patch, `feat!:` or `BREAKING CHANGE:` = major (document in `CONTRIBUTING.md`) (30 min)
- [ ] Add semantic-release step to CI workflow: runs only on push to `main`, after all tests pass (30 min)
- [ ] Create test release: push `feat: add product search` commit → verify 1.1.0 tag created and CHANGELOG updated (30 min)
- [ ] Re-tag Docker images with semver after release step (30 min)
- [ ] Verify image `ghcr.io/<org>/<service>:1.1.0` exists in GHCR (20 min)

---

#### Day 84 — Terraform (LocalStack) for infrastructure
**Daily Time Budget: ~5.5h**

- [ ] Install Terraform CLI + `localstack` (LocalStack simulates AWS locally) (20 min)
- [ ] Add LocalStack to `docker-compose.yml` — runs fake AWS services (S3, RDS, ECR) locally (20 min)
- [ ] Write `terraform/main.tf` — provider `aws`, endpoint = LocalStack: define `aws_db_instance` per service (or use `aws_rds_cluster`) (1.5h)
- [ ] Write `terraform/variables.tf` — parameterize DB names, instance types, storage sizes (30 min)
- [ ] Write `terraform/outputs.tf` — output connection strings (30 min)
- [ ] Run `terraform init && terraform apply` against LocalStack — verify RDS instances created (45 min)
- [ ] Document: in production, replace LocalStack endpoint with real AWS (30 min)
- [ ] Write ADR-020: "Terraform for IaC" — reason: version-controlled infrastructure, no drift (30 min)

---

#### Day 85 — Coverage hardening & test gap analysis
**Daily Time Budget: ~5h**

- [ ] Run `pytest --cov --cov-report=html` for each service — open coverage report in browser (30 min)
- [ ] Identify uncovered lines in each service (30 min)
- [ ] Write missing tests to bring each service to ≥80% coverage: focus on error paths and edge cases (2h)
- [ ] Add `codecov.yml` — configure coverage threshold and post coverage comment on PRs (30 min)
- [ ] Write `test_health_endpoint` for every service (5 services × 5 min = 25 min)
- [ ] Run full suite to confirm ≥80% across the board (30–60 min)

---

#### Day 86 — Phase review & CI documentation
**Daily Time Budget: ~4.5h**

- [ ] Write `docs/ci_cd.md` — document CI pipeline stages, how to add a new service, how to skip CI for docs-only commits (`[skip ci]`) (1h)
- [ ] Write `CONTRIBUTING.md` — commit message convention, PR process, coverage requirements (30 min)
- [ ] Run `docker compose up` from scratch on a clean machine (simulate with `docker system prune`) — confirm full stack starts (1h)
- [ ] Run `ruff`, `mypy`, `pytest` locally one final time — all green (30 min)
- [ ] Update top-level `README.md` with CI badge, Docker setup, service port map (30 min)

---

### Frontend Tasks
- [ ] Add `npm test -- --watchAll=false` to CI (15 min)
- [ ] Add `tsc --noEmit` to CI (10 min)
- [ ] Add eslint to CI (20 min)

### Database Changes
- [ ] Terraform provisions PostgreSQL instances (IaC only, no schema changes) (1.5h)

### DevOps & Infrastructure Tasks
- [ ] Multi-stage Dockerfiles for all 8 services (3h total)
- [ ] `.dockerignore` for all services (30 min)
- [ ] GitHub Actions CI workflows per service (2h)
- [ ] Trivy image scanning in CI (45 min)
- [ ] GHCR image push on main (30 min)
- [ ] Semantic release configuration (1h)
- [ ] Terraform + LocalStack setup (2h)

### Testing Tasks
- [ ] Coverage ≥80% for all services (2h total)
- [ ] `test_health_endpoint` for each service (25 min total)
- [ ] Integration tests run in CI using docker-compose.ci.yml (45 min)
- [ ] `test_ci_pipeline_fails_on_lint_error` (manual verification via bad commit) (20 min)
- [ ] `test_trivy_fails_on_critical_cve` (manual verification) (15 min)

### Architecture Improvements
- [ ] ADR-020: Terraform for Infrastructure as Code
- [ ] ADR-021: Multi-stage Docker builds for smaller production images
- [ ] Document image size targets in `docs/docker/image_sizes.md`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 80 | Multi-stage Dockerfiles | 5h |
| 81 | GitHub Actions CI per service | 5.5h |
| 82 | Docker build + image scan in CI | 5h |
| 83 | Semantic versioning & GitHub Releases | 5h |
| 84 | Terraform (LocalStack) for infrastructure | 5.5h |
| 85 | Coverage hardening & test gap analysis | 5h |
| 86 | Phase review & CI documentation | 4.5h |
| **Total** | | **~35.5h** |

### Expected Deliverables
- [ ] All services have multi-stage Dockerfiles with images < 200MB
- [ ] GitHub Actions CI runs for all 8 services on every push
- [ ] Trivy scans images for CVEs
- [ ] Semantic versioning with CHANGELOG and GitHub Releases
- [ ] Terraform provisions infrastructure against LocalStack

### Definition of Done
- [ ] `git push` triggers CI for all services within 30 seconds
- [ ] Coverage gate blocks merge if below 80%
- [ ] Image sizes documented and all under 200MB
- [ ] Terraform apply succeeds against LocalStack without errors

### Pitfalls to Avoid
- Multi-stage build: do not copy `.git` directory into runtime image — use `.dockerignore`
- Trivy: `--exit-code 1` fails the build; use `--ignore-unfixed` to skip CVEs with no fix yet
- Semantic release requires at least one conventional commit to generate a new version
- LocalStack does not perfectly emulate all AWS APIs — test against real AWS before production

### Interview Readiness
- What is a multi-stage Docker build and what problem does it solve?
- Explain CI/CD pipeline design — what runs in parallel vs sequentially?
- What is semantic versioning and what are conventional commits?
- What is Terraform and what does "infrastructure as code" mean?
- How do you enforce code coverage in a CI pipeline?
- What is an image scanner (Trivy) and what does it check?

---

## Phase 12: Days 87–93 — Kubernetes, Helm & Autoscaling

**Phase objective:** Deploy all services to a local Kubernetes cluster (kind or minikube), package them with Helm charts, configure HPA for autoscaling, and validate zero-downtime rolling updates.

---

### Project Architecture

**Architecture style:** Full microservices in Kubernetes

**What changed from Phase 11:**
- Added: Kubernetes layer (kind/minikube local cluster)
- Added: Helm charts for all services
- Added: HPA (Horizontal Pod Autoscaler) on gateway and catalog-service
- Added: Liveness and readiness probes on all pods
- Added: Ingress controller (Nginx Ingress)
- Added: Kubernetes CronJob for nightly recommendation job

**System diagram (end of Phase 12):**
```
[Browser]
    | HTTPS
    ↓
[Nginx Ingress Controller]
    | HTTP routing by path
    ↓
[Kubernetes Cluster (kind/minikube)]
    ├── Namespace: ecommerce-prod
    │    ├── Pod: api-gateway (FastAPI) ×2 replicas — HPA (1-5)
    │    ├── Pod: auth-service (FastAPI) ×2
    │    ├── Pod: catalog-service (Django/DRF) ×2 — HPA (1-4)
    │    ├── Pod: order-service (FastAPI) ×2
    │    ├── Pod: payment-service (FastAPI) ×2
    │    ├── Pod: delivery-warehouse (Django/DRF) ×1
    │    ├── Pod: notification-service (FastAPI) ×2
    │    ├── Pod: product-activity-monitor (Flask) ×1
    │    ├── Pod: celery-worker ×2
    │    └── CronJob: nightly-recommendations (02:00 UTC)
    │
    ├── Namespace: ecommerce-infra
    │    ├── StatefulSet: PostgreSQL (per service — or RDS in prod)
    │    ├── StatefulSet: Redis
    │    ├── StatefulSet: RabbitMQ
    │    ├── StatefulSet: Kafka
    │    ├── StatefulSet: Elasticsearch
    │    ├── StatefulSet: MongoDB
    │    └── StatefulSet: MinIO
    │
    └── [GitHub Container Registry] → images pulled into cluster

[HPA] → scales api-gateway and catalog-service based on CPU/RPS
```

**Data flow — Rolling update with zero downtime:**
1. CI builds new image tag `1.2.0` → pushes to GHCR
2. `helm upgrade api-gateway charts/api-gateway --set image.tag=1.2.0`
3. Kubernetes creates new pod (v1.2.0), waits for readiness probe to pass
4. Kubernetes terminates old pod (v1.1.0) with SIGTERM, waits `terminationGracePeriodSeconds=30`
5. Traffic shifts gradually via Service load balancer
6. Zero dropped requests (existing requests finish on old pod)

---

### Business Features
- [ ] All services deployed to Kubernetes with proper resource limits
- [ ] Gateway and catalog-service auto-scale under load
- [ ] Zero-downtime rolling update verified
- [ ] Nightly recommendation job runs as Kubernetes CronJob

---

#### Day 87 — kind cluster setup & Nginx Ingress
**Daily Time Budget: ~5h**

- [ ] Install `kind` and `kubectl` locally (20 min)
- [ ] Write `kind-config.yaml` — 1 control plane + 2 worker nodes (15 min)
- [ ] Run `kind create cluster --config kind-config.yaml` (10 min)
- [ ] Install Nginx Ingress Controller: `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/...` (20 min)
- [ ] Write `k8s/namespaces.yaml` — create `ecommerce-prod` and `ecommerce-infra` namespaces (15 min)
- [ ] Write `k8s/configmaps/` and `k8s/secrets/` — base env vars for each service (1h)
- [ ] Write `k8s/infra/postgres.yaml` — StatefulSet for PostgreSQL (or one per service) (1.5h)
- [ ] Apply infra manifests — verify pods running (30 min)

---

#### Day 88 — Helm charts: API Gateway & Auth Service
**Daily Time Budget: ~5.5h**

- [ ] Install Helm v3 (10 min)
- [ ] Write `charts/api-gateway/Chart.yaml`, `values.yaml`, `templates/deployment.yaml`, `templates/service.yaml`, `templates/ingress.yaml`, `templates/hpa.yaml` (2h)
- [ ] Write `charts/auth-service/` — same structure, no HPA (1.5h)
- [ ] Add liveness probe: `GET /health` — initialDelaySeconds=10, periodSeconds=10, failureThreshold=3 (30 min)
- [ ] Add readiness probe: `GET /ready` — initialDelaySeconds=5, periodSeconds=5 (30 min)
- [ ] Set resource limits: `requests: {cpu: 100m, memory: 128Mi}`, `limits: {cpu: 500m, memory: 512Mi}` (20 min)
- [ ] `helm install api-gateway charts/api-gateway` — verify pods running (30 min)

---

#### Day 89 — Helm charts: all remaining services
**Daily Time Budget: ~5.5h**

- [ ] Write charts for: `catalog-service`, `order-service`, `payment-service`, `notification-service`, `delivery-warehouse-service`, `product-activity-monitor`, `celery-worker` (3h)
- [ ] Write `charts/celery-worker/templates/deployment.yaml` — no ingress, only consumes RabbitMQ (30 min)
- [ ] Write `charts/nightly-recommendations/templates/cronjob.yaml` — `schedule: "0 2 * * *"`, `concurrencyPolicy: Forbid` (30 min)
- [ ] Install all charts — `helm install <name> charts/<name>` for each (30 min)
- [ ] Verify all pods: `kubectl get pods -n ecommerce-prod` — all Running (30 min)

---

#### Day 90 — HPA & resource limits
**Daily Time Budget: ~5h**

- [ ] Write HPA for `api-gateway`: `minReplicas: 1, maxReplicas: 5, targetCPUUtilizationPercentage: 70` (30 min)
- [ ] Write HPA for `catalog-service`: `minReplicas: 1, maxReplicas: 4` (20 min)
- [ ] Install metrics-server in kind cluster: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml` (20 min)
- [ ] Run Locust against Kubernetes cluster (via Ingress) — ramp to 100 users — watch HPA scale pods up (1h)
- [ ] Observe `kubectl get hpa -w` — verify scale-out triggers (20 min)
- [ ] Verify scale-down after load subsides (wait 5 min) (10 min)
- [ ] Set `PodDisruptionBudget` for api-gateway: `minAvailable: 1` (30 min)
- [ ] Write test: `test_hpa_scales_under_load` (Locust + kubectl assertion) (1h)
- [ ] Document HPA behavior in `docs/kubernetes/hpa.md` (30 min)

---

#### Day 91 — Zero-downtime rolling update
**Daily Time Budget: ~5h**

- [ ] Set `strategy: RollingUpdate, maxSurge: 1, maxUnavailable: 0` in all deployments (30 min)
- [ ] Set `terminationGracePeriodSeconds: 30` — allows in-flight requests to finish (20 min)
- [ ] Add `preStop: exec: sleep 5` — prevents race between SIGTERM and iptables update (20 min)
- [ ] Test rolling update: start Locust at 50 users, run `helm upgrade api-gateway` with new image tag — verify zero 5xx errors in Locust output (1.5h)
- [ ] If errors found: tune `readinessProbe.initialDelaySeconds` until clean (30–60 min)
- [ ] Document rolling update procedure in `docs/kubernetes/rolling_update.md` (30 min)
- [ ] Write `test_rolling_update_no_downtime` — automated with ab/wrk (1h)

---

#### Day 92 — Ingress routing & TLS
**Daily Time Budget: ~5h**

- [ ] Write `k8s/ingress.yaml` — route `/api/v1/catalog/*` → catalog-service, `/api/v1/auth/*` → auth-service, etc. (1h)
- [ ] Configure Nginx Ingress rate limiting annotations (supplement Redis rate limiting) (30 min)
- [ ] Set up self-signed TLS cert for local dev: `openssl req -x509 ...`, create `kubectl create secret tls` (45 min)
- [ ] Configure Ingress with `tls:` block (20 min)
- [ ] Test HTTPS access to all routes in browser (ignore self-signed warning) (30 min)
- [ ] Write `README.md` update: local Kubernetes quickstart with `kind` (45 min)
- [ ] Test end-to-end: React (local :3000) → Ingress → pods → DB (30 min)

---

#### Day 93 — CronJob + Helm umbrella chart
**Daily Time Budget: ~4.5h**

- [ ] Write `charts/nightly-recommendations/templates/cronjob.yaml` — test locally by setting schedule to `*/1 * * * *`, verify job runs and produces recommendations (45 min)
- [ ] Reset schedule to `0 2 * * *` and set `concurrencyPolicy: Forbid` (10 min)
- [ ] Write Helm umbrella chart `charts/ecommerce/` — includes all sub-charts as dependencies in `Chart.yaml` (1h)
- [ ] Test `helm install ecommerce charts/ecommerce` — installs entire stack in one command (45 min)
- [ ] Run full Locust load test against Kubernetes — document p95 latency (30 min)
- [ ] Write ADR-022: "Kubernetes for container orchestration" — HPA, rolling updates, namespace isolation (30 min)

---

### Frontend Tasks
- [ ] Update React `VITE_API_URL` to point to Kubernetes Ingress (10 min)
- [ ] Verify all pages work via Kubernetes (30 min)

### Database Changes
- [ ] StatefulSets for all databases in Kubernetes (included in Day 87) (1.5h)
- [ ] PersistentVolumeClaims for each database StatefulSet (30 min)

### DevOps & Infrastructure Tasks
- [ ] kind cluster config + setup (45 min)
- [ ] Nginx Ingress controller install (20 min)
- [ ] Helm charts for all 8 services (5h total)
- [ ] HPA manifests for gateway and catalog (30 min)
- [ ] PodDisruptionBudget for critical services (30 min)
- [ ] Umbrella Helm chart (1h)
- [ ] CronJob for nightly recommendations (30 min)

### Testing Tasks
- [ ] `test_all_pods_running` — `kubectl get pods` all Running/Ready (20 min)
- [ ] `test_hpa_scales_under_load` (1h)
- [ ] `test_rolling_update_zero_5xx` (1h)
- [ ] `test_cronjob_runs_successfully` (30 min)
- [ ] `test_ingress_routes_correctly` (20 min)
- [ ] `test_pdb_prevents_full_eviction` (30 min)

### Architecture Improvements
- [ ] ADR-022: Kubernetes for container orchestration
- [ ] Document pod resource sizing decisions in `docs/kubernetes/resource_sizing.md`
- [ ] Document Helm chart values override strategy (dev vs prod values files)

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 87 | kind cluster setup & Nginx Ingress | 5h |
| 88 | Helm charts: API Gateway & Auth Service | 5.5h |
| 89 | Helm charts: all remaining services | 5.5h |
| 90 | HPA & resource limits | 5h |
| 91 | Zero-downtime rolling update | 5h |
| 92 | Ingress routing & TLS | 5h |
| 93 | CronJob + Helm umbrella chart | 4.5h |
| **Total** | | **~35.5h** |

### Expected Deliverables
- [ ] Entire stack running in Kubernetes via `helm install ecommerce charts/ecommerce`
- [ ] HPA verified: api-gateway scales from 1 to 5 replicas under load
- [ ] Zero 5xx errors during rolling update
- [ ] Nightly CronJob verified
- [ ] HTTPS via Nginx Ingress working locally

### Definition of Done
- [ ] `helm install ecommerce charts/ecommerce` deploys all services in one command
- [ ] All pods pass liveness and readiness probes
- [ ] Rolling update with zero downtime verified by Locust
- [ ] HPA scales gateway under CPU load

### Pitfalls to Avoid
- `maxUnavailable: 0` + `maxSurge: 1` requires enough cluster capacity for the extra pod during rollout
- HPA requires `metrics-server` — do not forget to install it in kind (it's not built-in)
- Django WSGI services need `gunicorn` not `uvicorn` in Kubernetes (WSGI vs ASGI)
- Do not set resource `limits.memory` too low for Django — it uses more memory than FastAPI under load
- `preStop: sleep 5` is critical — without it, Kubernetes removes the pod from iptables before traffic drains

### Interview Readiness
- What is Kubernetes HPA and what metrics can it scale on?
- Explain liveness vs readiness probe — what happens when each fails?
- What is a PodDisruptionBudget and why do you need it?
- Explain a Kubernetes rolling update — how does zero downtime work?
- What is a Helm chart and what does it contain?
- What is a CronJob in Kubernetes and how does `concurrencyPolicy: Forbid` work?

---

## Phase 13: Days 94–100 — Observability, Resilience & Portfolio Readiness

**Phase objective:** Wire up full observability (Prometheus, Grafana, Loki, OpenTelemetry, Sentry), add resilience patterns (circuit breaker, bulkhead, retry with jitter), run a chaos test, complete OWASP security review, and produce a portfolio-ready README, architecture diagram, and 10 ADRs.

---

### Project Architecture

**Architecture style:** Full microservices with event-driven core + full observability

**What changed from Phase 12:**
- Added: Prometheus scraping all services
- Added: Grafana dashboards (RED metrics, Saga state, cache hit ratio)
- Added: OpenTelemetry tracing across all services (distributed traces)
- Added: Loki log aggregation
- Added: Jaeger (or Tempo) for trace visualization
- Added: Sentry for error tracking
- Added: Circuit breaker, bulkhead, retry with jitter

**System diagram (end of Phase 13 — FINAL):**
```
[Browser]
    | HTTPS
    ↓
[Nginx Ingress]
    ↓
[Kubernetes Cluster]
    ├── [API Gateway (FastAPI)] → traces → [Jaeger/Tempo]
    ├── [Auth Service (FastAPI)] → errors → [Sentry]
    ├── [Catalog Service (Django/DRF)] → metrics → [Prometheus]
    ├── [Order Service (FastAPI)] + Circuit Breaker → Payment
    ├── [Payment Service (FastAPI)]
    ├── [Delivery & Warehouse (Django/DRF)] + Django Admin
    ├── [Notification Service (FastAPI)] ← Kafka consumer
    ├── [Product Activity Monitor (Flask)] ← Kafka consumer
    └── [Celery Worker]

[Observability Stack]
    ├── Prometheus :9090 ← scrapes /metrics from all services
    ├── Grafana :3001 ← dashboards: RED metrics, Saga states, cache hits
    ├── Loki :3100 ← receives structured JSON logs from all services
    ├── Promtail → pushes logs to Loki
    ├── Jaeger/Tempo ← receives OTel traces via OTLP
    └── Sentry (cloud SaaS) ← receives exception reports

[Persistence Layer]
    ├── 6× PostgreSQL (per service)
    ├── MongoDB :27017
    ├── Elasticsearch :9200
    ├── Redis :6379
    ├── RabbitMQ :5672
    ├── Kafka :9092
    └── MinIO :9000
```

**Data flow — Distributed trace for Checkout:**
1. React → POST /checkout — OTel SDK creates root span `checkout.request` with `trace_id`
2. API Gateway injects `traceparent` header → Order Service
3. Order Service creates child span `order.create`, calls Payment Service with `traceparent`
4. Payment Service creates child span `payment.process`
5. All spans sent to Jaeger via OTLP
6. Grafana → Jaeger → visualize full trace waterfall: gateway → order → payment → total 340ms

---

### Business Features
- [ ] Grafana dashboard shows p50/p95/p99 latency for each service
- [ ] Grafana shows Kafka consumer lag per topic
- [ ] Full distributed trace visible in Jaeger for any checkout request
- [ ] Errors from any service surface in Sentry with stack trace
- [ ] Circuit breaker prevents cascade failure when Payment Service is down

---

#### Day 94 — Prometheus + Grafana RED metrics
**Daily Time Budget: ~5h**

- [ ] Add `prometheus-client` to all FastAPI services — expose `/metrics` endpoint (30 min)
- [ ] Add `django-prometheus` to Django services — auto-instruments Django ORM, requests (30 min)
- [ ] Add Flask `prometheus_flask_exporter` to product-activity-monitor (15 min)
- [ ] Deploy Prometheus to Kubernetes (`kube-prometheus-stack` Helm chart) (45 min)
- [ ] Write `prometheus.yml` scrape configs for all services (30 min)
- [ ] Deploy Grafana — configure Prometheus as data source (20 min)
- [ ] Write Grafana dashboard (JSON or via UI): RED metrics per service — Rate (req/s), Error rate (%), Duration (p95) (1.5h)
- [ ] Add custom metric: `saga_state_total{state}` counter — increment per saga state transition (30 min)
- [ ] Add custom metric: `cache_hit_total` and `cache_miss_total` in `CacheService` (20 min)

---

#### Day 95 — OpenTelemetry distributed tracing
**Daily Time Budget: ~5.5h**

- [ ] Install `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`, `opentelemetry-exporter-otlp` in all FastAPI services (30 min)
- [ ] Install `opentelemetry-instrumentation-django` in Django services (20 min)
- [ ] Deploy Jaeger (or Grafana Tempo) to Kubernetes (30 min)
- [ ] Configure OTel SDK in each service: `TracerProvider` → OTLP exporter → Jaeger (1h)
- [ ] Auto-instrument FastAPI with `FastAPIInstrumentor().instrument_app(app)` (20 min)
- [ ] Auto-instrument Django with `DjangoInstrumentor().instrument()` in `manage.py` (20 min)
- [ ] Add manual spans in checkout saga orchestrator steps (1h)
- [ ] Propagate `traceparent` through Kafka message headers (45 min)
- [ ] Verify in Jaeger UI: trigger a checkout → find trace → see full waterfall (30 min)

---

#### Day 96 — Loki log aggregation
**Daily Time Budget: ~5h**

- [ ] Deploy Loki + Promtail to Kubernetes (Grafana Loki Helm chart) (45 min)
- [ ] Configure Promtail to scrape pod logs from all namespaces and push to Loki (30 min)
- [ ] Ensure all services output structured JSON logs (structlog in FastAPI, `python-json-logger` in Django, Flask) (1h)
- [ ] Add Loki as data source in Grafana (10 min)
- [ ] Write Grafana Loki query: show all ERROR logs across all services in last 1h (30 min)
- [ ] Write Grafana correlation panel: click on metric spike → auto-link to Loki logs at that time (1h)
- [ ] Verify: trigger a 500 error → find it in Loki within 10 seconds (30 min)

---

#### Day 97 — Sentry error tracking
**Daily Time Budget: ~5h**

- [ ] Sign up for Sentry (free tier) or deploy self-hosted Sentry (sentry.io) (15 min)
- [ ] Install `sentry-sdk[fastapi]` in all FastAPI services — initialize with DSN in settings (30 min)
- [ ] Install `sentry-sdk[django]` in Django services (20 min)
- [ ] Install `sentry-sdk[flask]` in product-activity-monitor (15 min)
- [ ] Configure: `traces_sample_rate=0.1`, `environment=production`, `release=<semver>` (30 min)
- [ ] Trigger a test exception in each service — verify all appear in Sentry dashboard (30 min)
- [ ] Write Sentry alert: notify (email/Slack) when error rate > 10/min in any service (20 min)
- [ ] Add Sentry `DSN` to Kubernetes Secrets, inject as env var (20 min)
- [ ] Write test: `test_sentry_captures_unhandled_exception` (mock Sentry SDK, assert `capture_exception` called) (1h)

---

#### Day 98 — Circuit breaker, bulkhead, retry with jitter
**Daily Time Budget: ~5.5h**

- [ ] Install `circuitbreaker` or implement manually using `tenacity` (15 min)
- [ ] Write `CircuitBreaker` wrapper around HTTP calls from Order Service to Payment Service: `@circuit(failure_threshold=5, recovery_timeout=30)` (1h)
- [ ] Write `retry_with_jitter(fn, max_attempts=3, base_delay=0.1)` using exponential backoff + random jitter via `tenacity` (1h)
- [ ] Apply retry to Kafka publish (transient network failures) and Notification Service HTTP calls (30 min)
- [ ] Write bulkhead: limit concurrent calls from Order Service to Payment Service using `asyncio.Semaphore(max_concurrent=10)` (45 min)
- [ ] Write test: `test_circuit_opens_after_5_failures` (30 min)
- [ ] Write test: `test_retry_succeeds_on_third_attempt` (30 min)
- [ ] Kill Payment Service pod mid-test — verify circuit breaker returns 503 fast (no 30s timeout) (30 min)
- [ ] Document ADR-023: "Circuit Breaker + Retry with Jitter" (30 min)

---

#### Day 99 — Chaos test + OWASP security review
**Daily Time Budget: ~5h**

- [ ] Write chaos test script: start Locust at 50 users → delete Payment Service pod with `kubectl delete pod` → verify circuit breaker activates → restart pod → verify recovery (1.5h)
- [ ] Document chaos test results in `docs/chaos_test.md` (30 min)
- [ ] OWASP Top 10 review — go through each item:
  1. Injection: parameterized queries everywhere? ✓ (SQLAlchemy)
  2. Broken Auth: JWT expiry, refresh rotation ✓
  3. Sensitive Data: passwords hashed, no tokens in logs ✓
  4. XXE: not applicable (no XML parsing)
  5. Broken Access Control: RBAC on every endpoint ✓
  6. Security Misconfiguration: check Docker images for root user
  7. XSS: React escapes by default ✓
  8. Insecure Deserialization: Pydantic validates all input ✓
  9. Vulnerable Components: Trivy scan ✓
  10. Insufficient Logging: Loki + Sentry ✓ (1.5h)
- [ ] Fix any OWASP gaps found (30–60 min)
- [ ] Add `Content-Security-Policy` header in Nginx (20 min)
- [ ] Confirm no service runs as root inside container — add `USER nonroot` to all Dockerfiles (30 min)

---

#### Day 100 — Portfolio readiness: README, ADRs, postmortem
**Daily Time Budget: ~5h**

- [ ] Write final `README.md`: system overview, architecture diagram (from Phase 13 diagram), tech stack table, setup instructions (docker compose + kubernetes), service port map (2h)
- [ ] Write 10 ADRs in `docs/adr/` (compile and polish all ADRs from previous phases: ADR-001 through ADR-023, select the 10 most significant) (1h)
- [ ] Write `docs/postmortem.md` — simulate a production incident: "Overselling due to missing FOR UPDATE — discovered in Phase 5 concurrency test. Root cause: optimistic assumption about stock. Fix: SELECT FOR UPDATE NOWAIT. Prevention: race-condition test added to CI." (30 min)
- [ ] Write `docs/architecture.md` — final service topology table (below) + evolution narrative (30 min)
- [ ] Run final `docker compose up` — verify entire stack starts from scratch (30 min)
- [ ] Run final `pytest` across all services — all green (30 min)

---

### Frontend Tasks
- [ ] Add error boundary in React — show generic "Something went wrong" on unexpected errors (30 min)
- [ ] Add network error handling — show "Unable to connect" when API gateway is unreachable (20 min)

### Database Changes
- [ ] No schema changes — all databases stable

### DevOps & Infrastructure Tasks
- [ ] Deploy Prometheus + Grafana via kube-prometheus-stack Helm chart (45 min)
- [ ] Deploy Loki + Promtail Helm chart (30 min)
- [ ] Deploy Jaeger/Tempo Helm chart (30 min)
- [ ] Add Sentry DSN to Kubernetes Secrets (15 min)
- [ ] Add `USER nonroot` to all Dockerfiles (20 min)
- [ ] Add `Content-Security-Policy` in Nginx config (15 min)

### Testing Tasks
- [ ] `test_prometheus_metrics_exposed` — GET /metrics returns 200 for each service (20 min)
- [ ] `test_otel_trace_created_on_request` — verify OTel span created (30 min)
- [ ] `test_sentry_captures_exception` (25 min)
- [ ] `test_circuit_breaker_opens` (30 min)
- [ ] `test_retry_with_jitter_succeeds` (25 min)
- [ ] `test_chaos_pod_kill_recovery` (1h)
- [ ] `test_owasp_no_sql_injection` — parameterized query test (20 min)

### Architecture Improvements
- [ ] ADR-023: Circuit Breaker + Retry with Jitter
- [ ] ADR-024: OpenTelemetry for distributed tracing (vendor-neutral)
- [ ] Final architecture diagram in `docs/architecture.md`

### Phase Time Summary

| Day | Focus | Est. Time |
|-----|-------|-----------|
| 94 | Prometheus + Grafana RED metrics | 5h |
| 95 | OpenTelemetry distributed tracing | 5.5h |
| 96 | Loki log aggregation | 5h |
| 97 | Sentry error tracking | 5h |
| 98 | Circuit breaker, bulkhead, retry | 5.5h |
| 99 | Chaos test + OWASP security review | 5h |
| 100 | Portfolio readiness: README, ADRs | 5h |
| **Total** | | **~36h** |

### Expected Deliverables
- [ ] Grafana dashboard with RED metrics for all services
- [ ] Distributed traces visible in Jaeger for checkout flow
- [ ] All service errors aggregated in Sentry
- [ ] Circuit breaker prevents cascade failure
- [ ] Chaos test documented with recovery time
- [ ] OWASP Top 10 checklist completed
- [ ] Final README, 10 ADRs, postmortem document

### Definition of Done
- [ ] Grafana shows all 8 services healthy with RED metrics
- [ ] Checkout trace visible in Jaeger with all service spans
- [ ] Circuit breaker test: pod killed → 503 returned in < 100ms (not 30s timeout)
- [ ] OWASP review: no critical gaps
- [ ] `docker compose up` and `helm install ecommerce` both work from clean checkout

### Pitfalls to Avoid
- OTel `trace_id` propagation through Kafka requires manual header injection — does not happen automatically
- Sentry `traces_sample_rate=1.0` in production is expensive — use 0.05–0.1
- Circuit breaker state is per-process — in Kubernetes with 2 replicas, each pod has independent state; use Redis for shared state if needed
- Grafana dashboards created via UI are not version-controlled — export as JSON and commit to repo

### Interview Readiness
- What is the RED method for monitoring? What are Rate, Error, Duration?
- Explain distributed tracing — what is a trace vs a span?
- What is OpenTelemetry and why is it vendor-neutral?
- Explain the circuit breaker pattern — what are the CLOSED, OPEN, HALF-OPEN states?
- What is exponential backoff with jitter and why add jitter?
- Walk through the OWASP Top 10 — which ones did you implement protection against?
- What is chaos engineering and what does it validate?

---

## Final Service Map (Day 100)

| Service | Framework | Language | DB | Communication | Introduced |
|---|---|---|---|---|---|
| API Gateway | FastAPI | Python | — | REST in, gRPC/HTTP out | Phase 1→8 |
| Auth Service | FastAPI | Python | PostgreSQL | gRPC | Phase 2 |
| Order Service | FastAPI | Python | PostgreSQL | REST + Kafka + Saga | Phase 5 |
| Payment Service | FastAPI | Python | PostgreSQL | gRPC + Kafka | Phase 6 |
| Notification Service | FastAPI | Python | PostgreSQL | Kafka consumer | Phase 7 |
| Catalog Service | Django/DRF | Python | PostgreSQL | REST + Kafka | Phase 8 |
| Delivery & Warehouse | Django/DRF | Python | PostgreSQL | REST + Kafka + Django Admin | Phase 8 |
| Product Activity Monitor | Flask | Python | MongoDB | Kafka consumer | Phase 9 |
| Celery Worker | Celery | Python | — | RabbitMQ | Phase 7 |
| Frontend | React/TS | JavaScript | — | REST → Gateway | Phase 1 |

---

## Architecture Evolution Summary

| Phase | Architecture Style | New Components |
|---|---|---|
| 1–2 | Single-process monolith | FastAPI + PostgreSQL + React |
| 3–4 | Modular monolith (bounded contexts) | Sellers, Variants, Inventory |
| 5–6 | Modular monolith + outbox pattern | Cart, Orders, Payments, Outbox |
| 7 | Modular monolith + async workers | Redis, Celery, RabbitMQ, Notification Service |
| 8 | Partial microservices | Catalog (Django), Delivery (Django), API Gateway, gRPC |
| 9 | Full microservices + event-driven | Kafka, Saga, CQRS, SSE, Flask+MongoDB |
| 10 | Polyglot persistence | Elasticsearch, MongoDB Reviews, MinIO |
| 11 | CI/CD hardened | GitHub Actions, multi-stage Docker, Terraform |
| 12 | Kubernetes | Helm, HPA, Rolling updates, Ingress |
| 13 | Fully observable + resilient | Prometheus, Grafana, OTel, Loki, Sentry, Circuit Breaker |

---

---

## ADR Index

All Architecture Decision Records produced over 100 days. Each lives in `docs/adr/ADR-NNN-slug.md`.

| # | Title | Phase | Key Decision |
|---|-------|-------|-------------|
| ADR-001 | SQLAlchemy async engine | 1 | Use `create_async_engine` + asyncpg over sync SQLAlchemy — FastAPI is ASGI; blocking DB calls block the event loop |
| ADR-002 | Alembic for migrations | 1 | Version-controlled schema history; `--autogenerate` catches most changes but always review output |
| ADR-003 | JWT access + DB refresh token | 2 | Stateless short-lived access token (15 min) + stateful long-lived refresh token (7 days) in DB |
| ADR-004 | Auth service always FastAPI | 2 | Auth requires async streaming of token validation; must never migrate to Django/WSGI |
| ADR-005 | Bounded context monolith | 3 | `app/domains/` separation prepares codebase for microservices extraction in Phase 8 without a big-bang rewrite |
| ADR-006 | Cursor pagination over OFFSET | 4 | OFFSET degrades as `O(offset)` on large tables; keyset cursor is `O(1)` with proper index |
| ADR-007 | Pessimistic locking for checkout | 5 | `SELECT FOR UPDATE NOWAIT` prevents overselling; optimistic locking would require retry loops at application layer |
| ADR-008 | Unit of Work pattern | 5 | Single `AsyncSession` per checkout transaction guarantees atomicity across cart, stock, and order repositories |
| ADR-009 | Transactional Outbox Pattern | 6 | Outbox event written in same DB TX as business write — guarantees at-least-once event delivery without distributed transactions |
| ADR-010 | Idempotency keys for payments | 6 | Payment networks retry; storing request fingerprint prevents double-charge |
| ADR-011 | Redis rate limiting | 7 | Sliding window via Redis INCR+EXPIRE is atomic and survives restarts; in-memory counters are not shared across replicas |
| ADR-012 | Notification Service as FastAPI | 7 | Channel registry pattern; async SMTP fits ASGI; decoupled from monolith domain logic |
| ADR-013 | Database-per-service | 8 | Schema ownership and independent deployability; shared DB creates invisible coupling between teams |
| ADR-014 | API Gateway as single entry point | 8 | Centralised JWT validation; clients call one host; downstream services trust the gateway |
| ADR-015 | Notification Service decoupled via Kafka | 9 | Adding new notification channels requires no changes to publishing services |
| ADR-016 | CQRS read model for order summaries | 9 | Denormalised `order_summaries` table avoids repeated expensive joins on the hot order-list endpoint |
| ADR-017 | Saga Pattern for distributed checkout | 9 | Choreography-based saga over 2PC — services remain independently deployable; compensation handles failures |
| ADR-018 | Elasticsearch for product search | 10 | PostgreSQL FTS cannot do faceted aggregations or relevance scoring at this scale cheaply |
| ADR-019 | MongoDB for reviews | 10 | Replies are naturally embedded sub-documents; flexible schema accommodates per-category metadata fields |
| ADR-020 | Terraform for IaC | 11 | Version-controlled infrastructure; drift detection; reproducible environments |
| ADR-021 | Multi-stage Docker builds | 11 | Separate builder and runtime stages reduce final image size by 60–70% and exclude build tools |
| ADR-022 | Kubernetes for orchestration | 12 | HPA, rolling updates, readiness probes, and namespace isolation justify the complexity over plain Docker Compose at this scale |
| ADR-023 | Circuit Breaker + Retry with Jitter | 13 | Circuit breaker prevents cascade failure; jitter prevents thundering herd on recovery |
| ADR-024 | OpenTelemetry for distributed tracing | 13 | Vendor-neutral; swap Jaeger for Tempo or DataDog without changing instrumentation code |

---

*Generated 2026-07-09 — Total estimated time: ~504h over 100 days (~5h/day average)*
