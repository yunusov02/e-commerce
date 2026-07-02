# AtlasCommerce — Detailed Sprint Implementation Plans

> Companion to the AtlasCommerce 15-Sprint Roadmap. Each sprint below is broken into atomic, step-by-step tasks across Business Features, Backend, Frontend, Database, DevOps/Infrastructure, Testing, Architecture Improvements, and Expected Deliverables — written the way a real sprint would be planned and ticketed at a company.

---

## Sprint 1 — Foundations: The Naive Product Catalog API

### Business Features
- [ ] Admin/seller can create a product with name, description, price, SKU.
- [ ] Admin/seller can create/edit/delete a category and assign products to it.
- [ ] Any visitor can browse a list of products and view a single product's detail page.
- [ ] Admin/seller can update and delete a product.

### Backend Tasks
- [ ] Initialize FastAPI project structure (`app/main.py`, `app/api/`, `app/models/`, `app/schemas/`).
- [ ] Install and configure SQLAlchemy + `asyncpg` driver for async Postgres access.
- [ ] Define `Product` SQLAlchemy model: `id`, `name`, `description`, `price`, `sku`, `category_id`, `created_at`, `updated_at`.
- [ ] Define `Category` SQLAlchemy model: `id`, `name`, `slug`, `parent_id` (nullable, self-referential).
- [ ] Create Pydantic schemas: `ProductCreate`, `ProductUpdate`, `ProductRead`, `CategoryCreate`, `CategoryRead`.
- [ ] Implement `POST /products` — create product.
- [ ] Implement `GET /products` — list products (no pagination yet, capped at 100).
- [ ] Implement `GET /products/{id}` — get single product (404 if not found).
- [ ] Implement `PUT /products/{id}` — full update.
- [ ] Implement `DELETE /products/{id}` — delete product.
- [ ] Implement `POST /categories`, `GET /categories`, `GET /categories/{id}`, `PUT /categories/{id}`, `DELETE /categories/{id}`.
- [ ] Add a DB session dependency (`get_db`) using `Depends`.
- [ ] Add global exception handler for 404 / validation errors returning consistent JSON error shape.
- [ ] Set up `structlog` (or stdlib logging with a JSON formatter) for request logging.

### Frontend Tasks
- [ ] Scaffold React + TypeScript project with Vite.
- [ ] Create a typed API client (`api/products.ts`, `api/categories.ts`) wrapping `fetch`.
- [ ] Build `ProductListPage` — grid of products with name, price, thumbnail placeholder.
- [ ] Build `ProductDetailPage` — single product view by ID (React Router route `/products/:id`).
- [ ] Build `CategoryListPage` — simple list of categories.
- [ ] Build a minimal `AdminProductForm` (create/edit) — no auth yet, open to anyone (auth arrives Sprint 2).
- [ ] Wire basic error/loading states for all pages.

### Database Changes
- [ ] Create Postgres database `atlascommerce`.
- [ ] Write Alembic init (`alembic init`), configure `env.py` for async engine.
- [ ] Write first migration: `products`, `categories` tables with FK `products.category_id → categories.id`.
- [ ] Add `UNIQUE` constraint on `products.sku`.
- [ ] Add index on `products.category_id`.
- [ ] Write a `seed.py` script inserting ~50 sample products across 5 categories for local dev.

### DevOps & Infrastructure Tasks
- [ ] Write `Dockerfile` for the FastAPI service (single-stage for now).
- [ ] Write `docker-compose.yml` with services: `api`, `postgres`.
- [ ] Add `.env.example` documenting required env vars (`DATABASE_URL`, etc.).
- [ ] Add `.gitignore` (venv, `__pycache__`, `.env`, node_modules).
- [ ] Initialize Git repo, push to GitHub, set up branch protection on `main`.
- [ ] Add a stub GitHub Actions workflow that just runs `pytest` on push (full CI arrives Sprint 12).

### Testing Tasks
- [ ] Configure `pytest` + `pytest-asyncio` + `httpx.AsyncClient` test client.
- [ ] Write a `conftest.py` fixture spinning up a test database (separate schema or Dockerized test Postgres).
- [ ] Unit test: `ProductCreate` schema rejects negative price.
- [ ] Integration test: `POST /products` creates a product and returns 201 with correct body.
- [ ] Integration test: `GET /products/{id}` returns 404 for nonexistent ID.
- [ ] Integration test: `DELETE /products/{id}` removes the product and a subsequent GET returns 404.
- [ ] Integration test: creating a product with a duplicate SKU returns 409/400, not a 500.

### Architecture Improvements
- [ ] N/A this sprint — intentionally naive (routes call the DB session directly). Document this as a known limitation to be refactored in Sprint 2.

### Expected Deliverables
- [ ] `docker compose up` brings up API + DB with one command.
- [ ] Swagger UI at `/docs` shows all 10 endpoints, testable interactively.
- [ ] React app running locally, listing and viewing seeded products.
- [ ] 8+ passing tests in CI.
- [ ] README with setup instructions and an architecture diagram (v0, single box).

---

## Sprint 2 — Layered Architecture, Auth & Migrations Done Right

### Business Features
- [ ] User can register with email + password.
- [ ] User can log in and receive an access token + refresh token.
- [ ] User can refresh an expired access token without re-entering credentials.
- [ ] User can log out (refresh token invalidated).
- [ ] Only authenticated sellers/admins can create/edit/delete products; browsing stays public.
- [ ] Role distinction: `customer`, `seller`, `admin`.

### Backend Tasks
- [ ] Define `User` model: `id`, `email` (unique), `hashed_password`, `role`, `is_active`, `created_at`.
- [ ] Add `passlib[bcrypt]` (or `argon2-cffi`) for password hashing; write `hash_password()` / `verify_password()`.
- [ ] Implement `POST /auth/register` — validates unique email, hashes password, creates user.
- [ ] Implement `POST /auth/login` — verifies credentials, issues JWT access token (15 min) + refresh token (7 days).
- [ ] Implement `POST /auth/refresh` — validates refresh token, issues new access token, rotates refresh token.
- [ ] Implement `POST /auth/logout` — revokes the refresh token (store revoked tokens or a token-version column on `User`).
- [ ] Implement `get_current_user` dependency that decodes JWT and loads the user.
- [ ] Implement `require_role(*roles)` dependency factory for role-based authorization.
- [ ] Protect `POST/PUT/DELETE /products` with `require_role("seller", "admin")`.
- [ ] **Refactor**: introduce `app/repositories/` (e.g., `ProductRepository`, `UserRepository`) — pure data-access classes with no business logic.
- [ ] **Refactor**: introduce `app/services/` (e.g., `ProductService`, `AuthService`) — business logic calling repositories, called by routers.
- [ ] **Refactor**: move all existing Sprint-1 route logic out of routers into `ProductService`.
- [ ] Add a `RequestIDMiddleware` that generates/propagates an `X-Request-ID` header and injects it into log context.
- [ ] Add CORS middleware configured for the frontend origin.

### Frontend Tasks
- [ ] Build `RegisterPage` with email/password form + validation.
- [ ] Build `LoginPage` with email/password form.
- [ ] Implement token storage strategy (httpOnly cookie preferred; document XSS trade-off if using localStorage).
- [ ] Implement an Axios/fetch interceptor that attaches `Authorization: Bearer <token>` and auto-refreshes on 401.
- [ ] Build `AuthContext`/hook exposing `user`, `login()`, `logout()`, `isAuthenticated`.
- [ ] Add `ProtectedRoute` wrapper redirecting unauthenticated users away from the admin product form.
- [ ] Show/hide "Add Product" button based on role.

### Database Changes
- [ ] Migration: create `users` table (`email` unique index, `role` as enum/string, `hashed_password`, `token_version` or `revoked_refresh_tokens` table).
- [ ] Add composite index on `(email)` for fast login lookups (already covered by unique constraint, verify it's used).
- [ ] Alembic migration review checklist added to README: always inspect autogenerated migrations before applying.

### DevOps & Infrastructure Tasks
- [ ] Add `JWT_SECRET`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS` to `.env.example`.
- [ ] Update `docker-compose.yml` if a Redis instance is needed for refresh-token/session storage (optional now, or DB-backed).
- [ ] Add `pre-commit` config running `ruff`, `black`, `mypy` on commit.

### Testing Tasks
- [ ] Unit test: `hash_password`/`verify_password` round-trip correctness.
- [ ] Unit test: `ProductService.create_product` with a **mocked** `ProductRepository` (proves service logic is testable without a DB).
- [ ] Integration test: register → login → access protected endpoint with token → succeeds.
- [ ] Integration test: access protected endpoint without token → 401.
- [ ] Integration test: access protected endpoint with a `customer`-role token → 403.
- [ ] Integration test: expired access token is rejected; refresh flow issues a new valid one.
- [ ] Integration test: duplicate email registration returns 409.
- [ ] Coverage report generated in CI; target ≥ 80%.

### Architecture Improvements
- [ ] Layered Architecture in place: `router → service → repository → model`.
- [ ] Repository interfaces defined as `Protocol`/ABC so services depend on abstractions, not SQLAlchemy directly.
- [ ] Document the layering decision and its testing benefit in `ARCHITECTURE.md`.

### Expected Deliverables
- [ ] Full auth flow working end-to-end from the React app (register → login → protected action → logout).
- [ ] Product endpoints refactored into 3 clean layers with zero SQL in routers.
- [ ] `ARCHITECTURE.md` v1 documenting the layered design.
- [ ] Updated Swagger docs showing auth-protected endpoints with the lock icon.

---

## Sprint 3 — Modular Monolith: Sellers, Attributes, Variants, Warehouses

### Business Features
- [ ] A `seller`-role user has a Seller profile (store name, description) auto-created or set up on first login.
- [ ] Sellers can define reusable Attributes (e.g., "Color", "Size") with allowed values.
- [ ] Sellers can create Product Variants (e.g., "Red / Large") that combine attribute values and have their own SKU/price/stock.
- [ ] Admin can create Warehouses (name, location).
- [ ] Stock is tracked per Variant per Warehouse.
- [ ] Sellers can only edit their own products/variants (ownership authorization).

### Backend Tasks
- [ ] Create `app/modules/catalog/`, `app/modules/sellers/`, `app/modules/inventory/` folders as bounded-context boundaries.
- [ ] Define `Seller` model: `id`, `user_id` (FK), `store_name`, `description`.
- [ ] Define `Attribute` model: `id`, `name` (e.g., "Color").
- [ ] Define `AttributeValue` model: `id`, `attribute_id`, `value` (e.g., "Red").
- [ ] Define `ProductVariant` model: `id`, `product_id`, `sku`, `price`, `attribute_value_ids` (join table `variant_attribute_values`).
- [ ] Define `Warehouse` model: `id`, `name`, `location`.
- [ ] Define `Stock` model: `id`, `variant_id`, `warehouse_id`, `quantity` (composite unique on `variant_id, warehouse_id`).
- [ ] Add `product.seller_id` FK; update `ProductService.create_product` to set it from `current_user`.
- [ ] Implement ownership check: `ProductService.update_product` raises 403 if `product.seller_id != current_user.seller.id` (unless admin).
- [ ] Implement `POST/GET /attributes`, `POST/GET /attributes/{id}/values`.
- [ ] Implement `POST /products/{id}/variants`, `GET /products/{id}/variants`, `PUT/DELETE /variants/{id}`.
- [ ] Implement `POST /warehouses`, `GET /warehouses`.
- [ ] Implement `PUT /variants/{id}/stock/{warehouse_id}` to set quantity.
- [ ] Implement `GET /products` "list with variants" endpoint written **naively** (loop + query per product) — intentionally, to reproduce N+1 for Sprint 4.
- [ ] Add a query-count logging utility (e.g., SQLAlchemy event listener counting `before_cursor_execute`) and log the count per request.
- [ ] Ensure each module (`catalog`, `sellers`, `inventory`) exposes only a small internal Python API to other modules — no direct cross-module ORM model imports.

### Frontend Tasks
- [ ] Build `SellerOnboardingForm` (store name/description) shown once after a seller registers.
- [ ] Build `AttributeManagerPage` for sellers to create attributes and values.
- [ ] Extend `AdminProductForm` to add variants (attribute-value combinations + SKU/price).
- [ ] Build `WarehouseListPage` (admin) and stock-editing UI per variant/warehouse.
- [ ] Update `ProductDetailPage` to show a variant selector (e.g., color/size dropdowns) reflecting available stock.

### Database Changes
- [ ] Migration: `sellers`, `attributes`, `attribute_values`, `product_variants`, `variant_attribute_values`, `warehouses`, `stock` tables.
- [ ] Add FK + `ON DELETE CASCADE` where appropriate (e.g., deleting a product deletes its variants).
- [ ] Add composite unique constraint `(variant_id, warehouse_id)` on `stock`.
- [ ] Write a seed script generating 100k products with 2–4 variants each and stock across 3 warehouses (used for Sprint 4 performance work).

### DevOps & Infrastructure Tasks
- [ ] Add a `make seed-large` (or equivalent script) to load the 100k-row dataset locally.
- [ ] Document local Postgres memory/shared_buffers tuning needed to comfortably run the large seed.

### Testing Tasks
- [ ] Unit test: `factory_boy` factories for `Product`, `Variant`, `Attribute`, `Seller`, `Warehouse`.
- [ ] Integration test: seller A cannot edit seller B's product (403).
- [ ] Integration test: creating a variant with an attribute-value combo that doesn't exist returns 400.
- [ ] Integration test: setting stock for a variant/warehouse pair, then updating it, doesn't create duplicate rows (unique constraint respected).
- [ ] Functional test: full flow — register seller → create product → create attribute/values → create variant → set stock → variant appears in product detail with correct stock.
- [ ] Write (and intentionally let fail/pass-with-warning) a test asserting the query count on `GET /products` — document the current (bad) count as the Sprint 4 baseline.

### Architecture Improvements
- [ ] Establish module boundary convention: each module's public interface lives in `module/__init__.py` or a `service.py`; other modules import only from there.
- [ ] Write a short ADR: "Why folders-as-bounded-contexts now, services later."

### Expected Deliverables
- [ ] Multi-attribute, multi-variant, multi-warehouse catalog working end-to-end in the UI.
- [ ] Documented, reproduced N+1 query problem with the exact query count logged (e.g., "247 queries for 50 products").
- [ ] 100k-row seed dataset available for performance testing.

---

## Sprint 4 — Query Performance, Eager Loading & Pagination

### Business Features
- [ ] Product list page supports fast browsing with "load more" (cursor pagination) instead of numbered pages.
- [ ] Product list and search responses stay fast (sub-100ms locally) regardless of catalog size.

### Backend Tasks
- [ ] Rewrite `GET /products` query using `selectinload`/`joinedload` for variants, attributes, and stock.
- [ ] Implement cursor-based pagination: `GET /products?cursor=<opaque>&limit=20`, encode cursor as base64 of `(created_at, id)`.
- [ ] Cap `limit` at a hard maximum (e.g., 100) and reject/clamp larger values.
- [ ] Add a `QueryCounter` test utility/middleware (dev-only) that asserts query count via a response header (`X-DB-Query-Count`) for use in tests.
- [ ] Add composite indices via migration: `(category_id, created_at)` for category browsing, `(product_id)` on `product_variants`, `(variant_id, warehouse_id)` on `stock` (verify it exists from Sprint 3).
- [ ] Rewrite the seller's "my products" endpoint similarly with eager loading.
- [ ] Add a `/health` endpoint checking DB connectivity (used later for readiness probes).

### Frontend Tasks
- [ ] Replace numbered pagination UI with infinite scroll / "Load more" button using the returned cursor.
- [ ] Add a loading skeleton for the product grid during fetch.
- [ ] Debounce any client-side filter inputs to avoid excessive requests.

### Database Changes
- [ ] Run `EXPLAIN ANALYZE` on the pre-optimization `GET /products` query; save output to `docs/performance/before.txt`.
- [ ] Run `EXPLAIN ANALYZE` after adding indices/eager loading; save to `docs/performance/after.txt`.
- [ ] Add the 3 composite indices identified above via a reviewed Alembic migration.
- [ ] Enable `pg_stat_statements` extension locally for ongoing query analysis.

### DevOps & Infrastructure Tasks
- [ ] Add a Locust or `wrk` script (`scripts/load_test_products.py`) hitting `GET /products` at increasing concurrency.
- [ ] Wire the load-test script into a manual CI job (not yet on every PR — full performance gating comes later).

### Testing Tasks
- [ ] Regression test: `GET /products` returns results in ≤ N queries (assert via `X-DB-Query-Count` header) — this test must fail if someone reintroduces N+1.
- [ ] Benchmark test (pytest-benchmark or a manual script) comparing before/after latency at 100k rows; assert after-latency is under a defined threshold.
- [ ] Integration test: cursor pagination returns non-overlapping, correctly-ordered pages across 5 consecutive requests.
- [ ] Integration test: requesting `limit=10000` is clamped to the max, not honored literally.

### Architecture Improvements
- [ ] Introduce explicit read-model DTOs (`ProductListItem`, `ProductDetail`) so each endpoint returns only the fields it needs — no more serializing full ORM graphs by accident.
- [ ] Document indexing strategy in `docs/performance/indexing-strategy.md`.

### Expected Deliverables
- [ ] `GET /products` at O(1)-ish query count regardless of result size, verified by a CI-enforced test.
- [ ] Documented before/after `EXPLAIN ANALYZE` output and load-test latency numbers in the repo.
- [ ] Cursor pagination live in both API and UI.

---

## Sprint 5 — Cart, Checkout & Transactional Integrity

### Business Features
- [ ] Logged-in user can add a product variant to their cart with a quantity.
- [ ] User can view, update quantity in, and remove items from their cart.
- [ ] User can proceed to checkout, which reserves stock and creates a pending order.
- [ ] Checkout correctly rejects the request (with a clear error) if stock is insufficient — even under concurrent buyers.

### Backend Tasks
- [ ] Define `Cart` model (`id`, `user_id`) and `CartItem` model (`id`, `cart_id`, `variant_id`, `quantity`).
- [ ] Implement `POST /cart/items` (add), `PATCH /cart/items/{id}` (update qty), `DELETE /cart/items/{id}` (remove), `GET /cart` (view).
- [ ] Implement `CartService.add_item` — validates variant exists and (soft) has stock somewhere before adding.
- [ ] Implement `UnitOfWork` context manager wrapping a DB transaction across repository calls (`async with uow:` … `await uow.commit()`).
- [ ] Implement `CheckoutService.checkout(cart_id)`:
  - [ ] Opens a transaction via `UnitOfWork`.
  - [ ] For each cart item, locks the relevant `stock` row with `SELECT ... FOR UPDATE`.
  - [ ] Verifies `quantity <= stock.quantity`; raises `InsufficientStockError` otherwise (rolls back).
  - [ ] Decrements `stock.quantity`.
  - [ ] Creates an `Order` (status `pending`) and `OrderItem` rows.
  - [ ] Clears the cart.
  - [ ] Commits the transaction.
- [ ] Explicitly set the transaction isolation level for checkout (`REPEATABLE READ` or rely on row locks under `READ COMMITTED` — pick one and document why).
- [ ] Add a version column (`stock.version`) as an alternative optimistic-locking path; implement a feature-flagged second checkout strategy using optimistic locking + retry for comparison.
- [ ] Map `InsufficientStockError` to a `409 Conflict` API response with item-level detail.

### Frontend Tasks
- [ ] Build `CartPage` — line items, quantity steppers, remove button, subtotal.
- [ ] Add "Add to Cart" button on `ProductDetailPage` with optimistic UI update (rolls back on API error).
- [ ] Build `CheckoutPage` — review cart, confirm button, loading state during checkout call.
- [ ] Handle and display the 409 "insufficient stock" error clearly, item by item.

### Database Changes
- [ ] Migration: `carts`, `cart_items`, `orders` (`id`, `user_id`, `status`, `created_at`), `order_items` (`id`, `order_id`, `variant_id`, `quantity`, `price_at_purchase`).
- [ ] Add `version` integer column to `stock` (default 0) for the optimistic-locking experiment.
- [ ] Add index on `cart_items.cart_id` and `order_items.order_id`.

### DevOps & Infrastructure Tasks
- [ ] Write `scripts/locust_checkout_race.py`: N concurrent simulated users all checking out the same variant with only M units of stock available.
- [ ] Add a Makefile target `make race-test` running the above against a freshly seeded low-stock variant.

### Testing Tasks
- [ ] Integration test: add item, update quantity, remove item — cart state correct at each step.
- [ ] Concurrency test: spin up 20 concurrent `asyncio` tasks checking out the last 5 units of a variant; assert exactly 5 succeed and 15 get a 409.
- [ ] Integration test (real Postgres, not SQLite) verifying `SELECT FOR UPDATE` actually blocks a second concurrent transaction until the first commits/rolls back.
- [ ] Regression test reproducing the Lost Update bug **without** the lock (temporarily disable it in a test branch) to prove the bug exists, then re-enable and prove it's fixed — document both results.
- [ ] Load test: run the Locust race script and record results (successes/failures/latency) in `docs/performance/checkout-race.md`.

### Architecture Improvements
- [ ] `UnitOfWork` pattern formalized as a reusable abstraction usable across Cart, Checkout, and future Order-related services.
- [ ] ADR: "Pessimistic locking (SELECT FOR UPDATE) vs optimistic locking (version column) for checkout — chosen approach and why."

### Expected Deliverables
- [ ] Checkout that never oversells under the 20-concurrent-user race test.
- [ ] `docs/incidents/lost-update-bug.md` — a written "incident report" describing the bug you intentionally caused, how you diagnosed it, and the fix.
- [ ] Working Cart + Checkout UI.

---

## Sprint 6 — Orders, Payments (Mock) & Outbox/Idempotency

### Business Features
- [ ] User can pay for a pending order (mock payment gateway) using an idempotency key from the client.
- [ ] Retrying the same payment request (e.g., due to a network blip) never results in a double charge.
- [ ] Order moves through a defined lifecycle: `pending → paid → fulfilled → completed`, or `cancelled`.
- [ ] User can view their order history and an individual order's status timeline.
- [ ] Every order status change is recorded in an audit log.

### Backend Tasks
- [ ] Define `Payment` model: `id`, `order_id`, `idempotency_key` (unique), `amount`, `status`, `provider_reference`.
- [ ] Define `OutboxEvent` model: `id`, `aggregate_type`, `aggregate_id`, `event_type`, `payload` (JSON), `created_at`, `published_at` (nullable).
- [ ] Define `AuditLog` model: `id`, `entity_type`, `entity_id`, `action`, `old_value`, `new_value`, `actor_id`, `created_at`.
- [ ] Implement `MockPaymentGateway` class simulating success/failure/timeout (configurable via a query param or random seed for testing).
- [ ] Implement `PaymentService.charge(order_id, idempotency_key, amount)`:
  - [ ] Checks for an existing `Payment` with the same `idempotency_key`; if found, returns its stored result instead of re-charging.
  - [ ] Otherwise calls `MockPaymentGateway`, persists the `Payment`, updates `Order.status`, writes an `OutboxEvent` (`PaymentSucceeded`/`PaymentFailed`) — all in one DB transaction.
- [ ] Implement `Order` state machine as an explicit class/enum with allowed transitions (`pending→paid`, `paid→fulfilled`, etc.) — reject illegal transitions with a clear error.
- [ ] Add an `AuditLogger` service hooked into every `Order.status` change (Observer-style: a small internal event, not yet Kafka).
- [ ] Implement `POST /orders/{id}/pay` (accepts `Idempotency-Key` header).
- [ ] Implement `GET /orders`, `GET /orders/{id}` (with status history from audit log).
- [ ] Implement a simple polling **outbox relay** (a background asyncio task or scheduled script) that reads unpublished `OutboxEvent` rows and marks them published (stub — actual Kafka publish arrives Sprint 9; for now, log them).

### Frontend Tasks
- [ ] Build `OrderHistoryPage` listing the user's orders with status badges.
- [ ] Build `OrderDetailPage` with a status timeline component (pending → paid → fulfilled → completed).
- [ ] Build `PaymentPage`/modal — generates a client-side idempotency key (UUID) once per checkout attempt and reuses it on retry.
- [ ] Handle payment failure states with a retry button that reuses the same idempotency key.

### Database Changes
- [ ] Migration: `payments` (unique index on `idempotency_key`), `outbox_events`, `audit_logs`.
- [ ] Add `status` enum/check-constraint on `orders.status` restricting to valid values.
- [ ] Add index on `outbox_events.published_at` (partial index `WHERE published_at IS NULL` for efficient relay polling).

### DevOps & Infrastructure Tasks
- [ ] Add the outbox relay as a separate process/entrypoint in `docker-compose.yml` (even though it just logs for now).
- [ ] Add a config flag to `MockPaymentGateway` to simulate a configurable failure rate for testing.

### Testing Tasks
- [ ] Integration test: paying an order with idempotency key `X` twice results in exactly one `Payment` row and one charge.
- [ ] Integration test: paying with two **different** idempotency keys for the same order is rejected (order already paid).
- [ ] Integration test: illegal state transition (e.g., `pending → fulfilled` directly) raises an error.
- [ ] Integration test: a failed payment leaves the order in a well-defined state (not stuck) and is retryable.
- [ ] Unit test: `Order` state machine rejects every invalid transition pair, accepts every valid one (parametrized test covering the full transition table).
- [ ] Verify audit log entries are created for every status change in an end-to-end order lifecycle test.

### Architecture Improvements
- [ ] Outbox Pattern formalized: outbox write happens in the *same* transaction as the business write (verified by a test that rolls back the whole transaction on a simulated failure and confirms no orphaned outbox row).
- [ ] ADR: "Why the Outbox Pattern instead of publishing events directly from application code."

### Expected Deliverables
- [ ] End-to-end order lifecycle working in the UI: checkout → pay → status timeline updates.
- [ ] Proven idempotency (test + manual demo of double-clicking "Pay" not double-charging).
- [ ] Outbox table populated correctly and relayed (logged) reliably.

---

## Sprint 7 — Caching, Redis & Performance Engineering

### Business Features
- [ ] Product detail and category listing pages load noticeably faster on repeat views.
- [ ] Login endpoint is protected against brute-force attempts via rate limiting.
- [ ] Product pages support HTTP-level caching (browsers/CDNs can skip re-fetching unchanged data).

### Backend Tasks
- [ ] Add Redis client (`redis.asyncio`) and a `CacheService` wrapper (`get`, `set`, `delete`, `get_or_set`).
- [ ] Implement cache-aside for `GET /products/{id}`: check Redis → on miss, query DB → populate Redis with TTL (e.g., 5 min).
- [ ] Implement cache-aside for category listing endpoints similarly.
- [ ] Implement cache invalidation: on `ProductService.update_product`/`delete_product`, explicitly delete the relevant Redis key(s).
- [ ] Add `ETag` generation (hash of the resource) and `Cache-Control` headers on product endpoints; handle `If-None-Match` to return `304 Not Modified`.
- [ ] Implement Redis-based rate limiting (Lua script or `redis-py`'s built-in token-bucket pattern) on `POST /auth/login` and `POST /auth/register` (e.g., 5 attempts/minute/IP).
- [ ] Add cache stampede protection: use a short-lived Redis lock (`SET NX PX`) so only one request repopulates a hot expired key while others wait/serve stale.
- [ ] Instrument cache hit/miss counters (simple in-memory counters exposed via a debug endpoint — real metrics arrive Sprint 14).

### Frontend Tasks
- [ ] Configure the fetch client to send `If-None-Match` using a previously stored `ETag` and handle `304` by reusing cached local data.
- [ ] Add a visible (dev-only) indicator showing cache hit/miss for demo purposes.

### Database Changes
- [ ] No schema changes this sprint — purely additive caching layer.
- [ ] Document which read endpoints are cached and their TTLs in `docs/caching-strategy.md`.

### DevOps & Infrastructure Tasks
- [ ] Add `redis` service to `docker-compose.yml` with AOF persistence enabled.
- [ ] Extend the Locust script from Sprint 4 to compare cached vs uncached latency at the same concurrency.
- [ ] Add `REDIS_URL` to `.env.example`.

### Testing Tasks
- [ ] Integration test: first `GET /products/{id}` is a cache miss (assert via a test-only header or counter); second call is a cache hit.
- [ ] Integration test: updating a product invalidates its cache — subsequent `GET` reflects the new data, not stale cached data.
- [ ] Integration test: 6th login attempt within a minute from the same IP is rate-limited (`429`).
- [ ] Integration test: `304 Not Modified` returned when `If-None-Match` matches current `ETag`.
- [ ] Load test: re-run the Sprint-4 product-list load test with caching enabled; document the latency/throughput improvement.

### Architecture Improvements
- [ ] `CacheService` introduced as an injectable dependency (mockable in tests) rather than a global Redis client scattered through code.
- [ ] Document the cache invalidation contract: "every write path that changes cached data must explicitly invalidate it" as a code-review rule.

### Expected Deliverables
- [ ] `docs/performance/caching-before-after.md` with measured latency/throughput numbers.
- [ ] Rate limiting demonstrably blocking brute-force login attempts.
- [ ] Cache hit ratio ≥ 80% on hot product pages under the load test.

---

## Sprint 8 — Async Python, Background Jobs & the GIL

### Business Features
- [ ] User receives an order-confirmation email after successful payment (simulated/logged email in dev).
- [ ] User can request a downloadable PDF invoice for a completed order, generated asynchronously.
- [ ] Failed background jobs (e.g., email send failure) automatically retry and eventually land in a dead-letter queue if they keep failing.

### Backend Tasks
- [ ] Add Celery + RabbitMQ broker configuration (`celery_app.py`, task routing config).
- [ ] Implement `send_order_confirmation_email` Celery task (logs/sends via a fake SMTP/console backend in dev).
- [ ] Implement `generate_invoice_pdf` Celery task producing a PDF (e.g., via `reportlab` or `weasyprint`) and storing it (local disk for now, S3/MinIO arrives Sprint 10).
- [ ] Trigger `send_order_confirmation_email.delay(order_id)` from `PaymentService.charge` after a successful payment (inside the outbox flow, not blocking the request).
- [ ] Configure Celery retry policy with exponential backoff (`autoretry_for`, `retry_backoff=True`, `max_retries`) on both tasks.
- [ ] Configure a dead-letter queue: after max retries, route the failed task/message to a `dlq` queue instead of silently dropping it.
- [ ] Implement `GET /orders/{id}/invoice` returning the generated PDF (or a "still generating" status if not ready).
- [ ] Write the CPU-bound benchmark script comparing: (a) `threading`, (b) `multiprocessing`, (c) plain `asyncio` for a batch image-resize task (use Pillow on seeded product images) — record wall-clock time for each.
- [ ] Audit all async route handlers for accidental blocking calls (e.g., synchronous `requests` instead of `httpx.AsyncClient`) and fix any found.

### Frontend Tasks
- [ ] Show a "Confirmation email sent" toast after successful payment.
- [ ] Build an "Download Invoice" button on `OrderDetailPage` that polls (or shows a spinner) until the PDF is ready, then triggers download.

### Database Changes
- [ ] Add `orders.invoice_path` (nullable) column to track generated invoice location.
- [ ] Add a `background_jobs` audit table (optional) logging task name, status, attempts, last_error — useful for the DLQ visibility deliverable.

### DevOps & Infrastructure Tasks
- [ ] Add `rabbitmq`, `celery_worker`, `celery_beat` (if scheduled tasks are needed), and `flower` services to `docker-compose.yml`.
- [ ] Configure Flower for job monitoring at a local port.
- [ ] Add `RABBITMQ_URL` / broker config to `.env.example`.

### Testing Tasks
- [ ] Unit test: `send_order_confirmation_email` task logic (using Celery's eager/task-always-eager test mode).
- [ ] Integration test: triggering payment enqueues the email task (assert via a mocked `.delay` call or an eager-mode assertion on side effects).
- [ ] Integration test: a task configured to always fail retries the expected number of times, then appears in the DLQ.
- [ ] Test: run the CPU-bound benchmark script and assert (in a documented report, not a strict CI gate) that multiprocessing outperforms threading for the image-resize workload — this is the empirical GIL proof.
- [ ] Test: an I/O-bound benchmark (e.g., 20 concurrent mock HTTP calls) shows asyncio/threading outperforming a naive sequential approach.

### Architecture Improvements
- [ ] Slow/non-critical-path work (email, PDF generation) fully decoupled from the request/response cycle.
- [ ] `docs/performance/gil-benchmark.md` documenting measured results and the practical rule derived from them ("use asyncio/threads for I/O-bound, multiprocessing for CPU-bound, in this codebase").

### Expected Deliverables
- [ ] Working async email + invoice pipeline visible in Flower.
- [ ] DLQ populated and inspectable when a task is forced to fail repeatedly.
- [ ] `docs/performance/gil-benchmark.md` with real numbers from your machine.

---

## Sprint 9 — Event-Driven Architecture: Kafka, Sagas & CQRS Foundations

### Business Features
- [ ] Placing an order automatically and reliably triggers inventory reservation and payment across independent processing steps.
- [ ] If payment fails after inventory was reserved, the reservation is automatically released (compensation) — no manual intervention needed.
- [ ] User-facing order status updates live in near real-time (via SSE) as the backend processes each step.
- [ ] A fast "Order Summary" view is available for dashboards without hitting the transactional Order tables directly.

### Backend Tasks
- [ ] Add `kafka-python` or `aiokafka` client; configure producer/consumer settings.
- [ ] Replace the Sprint-6 stub outbox relay with a real relay that publishes `OutboxEvent` rows to Kafka topics (`orders`, `inventory`, `payments`) and marks them published on success.
- [ ] Define event schemas (e.g., Pydantic models) for `OrderCreated`, `InventoryReserved`, `InventoryReservationFailed`, `PaymentSucceeded`, `PaymentFailed`.
- [ ] Implement `SagaOrchestrator` service:
  - [ ] Consumes `OrderCreated` → calls Inventory reservation logic → publishes `InventoryReserved`/`InventoryReservationFailed`.
  - [ ] Consumes `InventoryReserved` → triggers `PaymentService.charge` → publishes `PaymentSucceeded`/`PaymentFailed`.
  - [ ] Consumes `PaymentFailed` → triggers a **compensation**: release the reserved stock, mark order `cancelled`.
  - [ ] Consumes `PaymentSucceeded` → marks order `paid`, triggers fulfillment step.
- [ ] Make every Kafka consumer idempotent: check (e.g., via a processed-event-ids table or the target entity's current state) before applying an event a second time.
- [ ] Implement a `read_model` projector consumer building a denormalized `order_summaries` table (CQRS read model) from the same event stream.
- [ ] Implement `GET /orders/{id}/stream` (SSE) pushing status updates as the saga progresses (backend publishes to connected clients via an in-process pub/sub or Redis Pub/Sub bridge).
- [ ] Add a consumer-group naming convention and document partition strategy for each topic (e.g., partition by `order_id` for ordering guarantees per order).

### Frontend Tasks
- [ ] Replace polling on `OrderDetailPage` with an `EventSource` (SSE) connection showing live status updates.
- [ ] Add a visual "processing" state machine indicator (reserving stock → charging payment → confirmed).
- [ ] Handle the compensation/cancellation case in the UI with a clear explanation to the user.

### Database Changes
- [ ] Migration: `order_summaries` (CQRS read table): `order_id`, `customer_email`, `total`, `status`, `item_count`, `updated_at`.
- [ ] Migration: `processed_events` table (`event_id` unique, `consumer_name`) for idempotent-consumer deduplication.
- [ ] Add `stock.reserved_quantity` column distinct from `stock.quantity` (available vs reserved) to support the reservation step cleanly.

### DevOps & Infrastructure Tasks
- [ ] Add `kafka` + `zookeeper` (or KRaft-mode Kafka) to `docker-compose.yml`.
- [ ] Add a topic-creation script/init container defining `orders`, `inventory`, `payments` topics with sensible partition counts.
- [ ] Add `kafdrop` or similar UI for local topic/message inspection.

### Testing Tasks
- [ ] Integration test (using an embedded/test Kafka broker or testcontainers): publish `OrderCreated`, assert `InventoryReserved` is eventually published and stock is decremented.
- [ ] Integration test: simulate `PaymentFailed` after `InventoryReserved` — assert the compensation releases the reservation and order becomes `cancelled`.
- [ ] Test: consuming the same `OrderCreated` event twice (simulating a Kafka redelivery) does not double-reserve stock (idempotency proof).
- [ ] Test: kill the saga orchestrator process mid-flow (simulated by stopping consumption), restart it, and assert the saga resumes correctly from Kafka's committed offset.
- [ ] Test: `order_summaries` read model matches the transactional `orders` table state after processing (eventual consistency verified within a timeout).

### Architecture Improvements
- [ ] Saga implemented as **orchestration** (central orchestrator), not choreography — document why in an ADR, including the alternative considered.
- [ ] CQRS read model formally separated: all dashboard/summary reads go through `order_summaries`, never the transactional tables.
- [ ] `docs/architecture/event-flow-diagram.md` showing the full `OrderCreated → ... → PaymentSucceeded/Failed → Compensation` flow.

### Expected Deliverables
- [ ] A full saga demo: place an order, watch it progress live via SSE, and a forced-payment-failure demo showing correct compensation.
- [ ] Kafdrop screenshots/log showing events flowing through topics.
- [ ] `docs/architecture/event-flow-diagram.md`.

---

## Sprint 10 — Search, Recommendations & Polyglot Persistence

### Business Features
- [ ] User can full-text search products by name/description with typo tolerance.
- [ ] User can filter search results by category, price range, and attributes (faceted search).
- [ ] Users can leave a review (rating + text, possibly with nested replies) on a product.
- [ ] Product detail page shows a "Customers also bought" section.
- [ ] Product images are stored in object storage, not the local filesystem.

### Backend Tasks
- [ ] Add Elasticsearch/OpenSearch client; define the `products` index mapping (name, description, category, price, attributes as nested/keyword fields).
- [ ] Extend the Sprint-9 outbox/Kafka pipeline: consume `ProductCreated`/`ProductUpdated`/`ProductDeleted` events to keep the ES index in sync (Adapter Pattern: `SearchIndexer` interface, ES implementation behind it).
- [ ] Implement `GET /search?q=...&category=...&min_price=...&max_price=...&attr_color=red` querying ES with filters + aggregations for facets.
- [ ] Add MongoDB client (Motor); define a `Review` document schema (`product_id`, `user_id`, `rating`, `text`, `replies: [...]`, `created_at`).
- [ ] Implement `POST /products/{id}/reviews`, `GET /products/{id}/reviews`, `POST /reviews/{id}/replies`.
- [ ] Add MinIO/S3 client; implement `POST /products/{id}/images` (upload) storing to object storage and saving the resulting URL on the product.
- [ ] Implement a nightly Celery task `compute_recommendations`: simple item-based collaborative filtering (co-purchase counts from `order_items`) writing results to a `recommendations` table/Redis cache.
- [ ] Implement `GET /products/{id}/recommendations` reading from the precomputed cache/table.
- [ ] Sanitize/validate all search query inputs before building the ES query DSL.

### Frontend Tasks
- [ ] Build `SearchPage` with a search-as-you-type input (debounced) and a facet sidebar (category, price range, attribute checkboxes).
- [ ] Build `ReviewSection` component on `ProductDetailPage` — list reviews, star rating input, reply threads.
- [ ] Build an image upload UI in the seller's product form with a preview.
- [ ] Add a `RecommendationCarousel` component on `ProductDetailPage`.

### Database Changes
- [ ] No new Postgres tables for reviews (moved to MongoDB) — document this decision.
- [ ] Add `recommendations` table (or Redis structure) storing `(product_id, recommended_product_id, score)`.
- [ ] Add `product.image_urls` (array/JSON column) referencing object-storage URLs.

### DevOps & Infrastructure Tasks
- [ ] Add `elasticsearch` (or `opensearch`), `mongodb`, and `minio` services to `docker-compose.yml`.
- [ ] Write an index-mapping versioning script (`scripts/create_index.py --version=v2`) to support safe reindexing without downtime.
- [ ] Add a Celery Beat schedule entry for the nightly recommendation job.

### Testing Tasks
- [ ] Integration test (testcontainers Elasticsearch): indexing a product then searching for it by partial name returns it.
- [ ] Integration test: updating a product's name re-syncs the ES index (eventually, within a timeout) and search reflects the new name.
- [ ] Integration test (testcontainers MongoDB): posting a review and a reply persists correctly and is retrievable in order.
- [ ] Test: search query with malicious/malformed input (e.g., ES query-DSL injection attempt) is safely handled, not passed through raw.
- [ ] Test: recommendation job produces non-empty results for a product with sufficient co-purchase history in seeded data.
- [ ] Relevance smoke test: searching an exact product name returns that product in the top 3 results.

### Architecture Improvements
- [ ] Polyglot persistence formalized: `docs/architecture/data-ownership.md` stating the source of truth for every entity (Postgres = orders/products/users; MongoDB = reviews; Elasticsearch = search index only, never source of truth; Redis = cache/recommendations).
- [ ] `SearchIndexer` interface allows swapping Elasticsearch for OpenSearch without touching `ProductService`.

### Expected Deliverables
- [ ] Working faceted search UI with sub-second results.
- [ ] Reviews with threaded replies live on product pages.
- [ ] "Customers also bought" populated from real seeded order data.
- [ ] `docs/architecture/data-ownership.md`.

---

## Sprint 11 — Splitting the Monolith: Microservices, API Gateway & gRPC

### Business Features
- [ ] The system behaves identically to the user, but Catalog and Payment now run and can be deployed as independent services.
- [ ] If the Catalog service is temporarily down, the rest of the site (cart, orders) keeps working with a clear degraded message on catalog-dependent pages.

### Backend Tasks
- [ ] Create two new deployable services: `catalog-service` and `payment-service`, each with its own FastAPI app, its own DB (or DB schema), and its own Dockerfile.
- [ ] Move `Product`, `Category`, `Attribute`, `Variant`, `Warehouse`, `Stock` models/logic into `catalog-service`.
- [ ] Move `Payment`, `MockPaymentGateway` logic into `payment-service`.
- [ ] Define `.proto` files for `CatalogService` (`GetProduct`, `CheckStock`) and `PaymentService` (`ChargePayment`) using Protocol Buffers.
- [ ] Generate gRPC stubs (`grpcio-tools`) for both services; implement the gRPC servers.
- [ ] Build a new `api-gateway` FastAPI service that:
  - [ ] Exposes the existing public REST API (unchanged external contract where possible).
  - [ ] Internally calls `catalog-service`/`payment-service` via gRPC clients instead of local function calls.
  - [ ] Implements a single GraphQL endpoint (`/graphql`, e.g., via Strawberry) for one aggregation use case: "order detail with product + seller info in one query."
- [ ] Implement `/health` (liveness) and `/ready` (readiness — checks DB + downstream dependency reachability) on every service.
- [ ] Implement graceful degradation in the Gateway: if `catalog-service` gRPC call times out, return cached/partial data with a `degraded: true` flag instead of a hard 500.
- [ ] Propagate a request/correlation ID through gRPC metadata across all services.

### Frontend Tasks
- [ ] Verify the frontend still talks only to the single Gateway URL — no direct calls to internal services.
- [ ] Add a UI banner/state for "some features temporarily unavailable" when the Gateway reports `degraded: true`.
- [ ] Wire the new GraphQL endpoint into the `OrderDetailPage` to replace 2 separate REST calls with one query.

### Database Changes
- [ ] Provision a separate Postgres database (or at minimum a separate schema with no cross-schema FKs) for `catalog-service` and one for `payment-service`.
- [ ] Migrate existing Catalog/Payment data into the new databases via a one-off migration script.
- [ ] Remove now-invalid cross-service foreign keys (e.g., `orders.variant_id` referencing a variant in a different DB) — replace with a plain non-FK reference + documented eventual-consistency contract.

### DevOps & Infrastructure Tasks
- [ ] Update `docker-compose.yml`: separate containers and DBs for `api-gateway`, `catalog-service`, `payment-service`, `order-service` (the remaining monolith), each with their own healthcheck.
- [ ] Add per-service `Dockerfile`s.
- [ ] Add a `docs/architecture/service-boundaries.md` diagram showing every service, its DB, and its gRPC/REST/Kafka interfaces.

### Testing Tasks
- [ ] Contract test (Pact or hand-rolled JSON schema check) between `api-gateway` and `catalog-service`'s gRPC contract — fails CI if either side changes the contract incompatibly.
- [ ] Contract test between `api-gateway` and `payment-service`.
- [ ] Integration test: full checkout flow works end-to-end across all 4 services running in Docker Compose.
- [ ] Resilience test: stop the `catalog-service` container mid-test, assert the Gateway returns a degraded-but-non-crashing response for catalog-dependent endpoints, and that Cart/Order endpoints (not dependent on Catalog) are unaffected.
- [ ] Test: `/health` and `/ready` return correct status codes when a dependency (e.g., DB) is intentionally disconnected.

### Architecture Improvements
- [ ] Service boundaries drawn along business capabilities (Catalog, Payment) — not technical layers — documented with the reasoning in an ADR.
- [ ] Explicit "no shared database" rule enforced and documented.
- [ ] `docs/architecture/service-boundaries.md` finalized with the full topology diagram.

### Expected Deliverables
- [ ] 4 independently deployable, independently testable services running together via Compose.
- [ ] Demonstrated graceful degradation when a non-critical service is killed.
- [ ] Contract tests passing in CI for every service boundary.

---

## Sprint 12 — CI/CD, Multi-Stage Docker & Infrastructure as Code

### Business Features
- [ ] N/A (internal engineering sprint) — but: every merged pull request results in a fully tested, deployable build with no manual steps, directly enabling faster, safer future feature delivery.

### Backend Tasks
- [ ] No new application features — audit and fix any lingering lint/type errors across all services in preparation for strict CI gates.
- [ ] Add `ruff`, `mypy --strict` (or a pragmatic strict subset), `black --check` as scripts (`make lint`) runnable identically locally and in CI.

### Frontend Tasks
- [ ] Add `eslint`, `prettier --check`, `tsc --noEmit` scripts.
- [ ] Configure a production build (`vite build`) and verify the output is deployable as static assets.

### Database Changes
- [ ] No schema changes — add a CI step that runs `alembic upgrade head` against a throwaway test DB and fails the build if any migration errors or drifts from models (`alembic check`/autogenerate diff is empty).

### DevOps & Infrastructure Tasks
- [ ] Convert every service's `Dockerfile` to a multi-stage build (builder stage with build deps → slim runtime stage with only what's needed); measure and record image size before/after per service.
- [ ] Write GitHub Actions workflow `ci.yml`: on every PR — checkout → cache dependencies → lint → type-check → unit tests → integration tests (with service containers) → build Docker images.
- [ ] Add `pip-audit` / `npm audit` (or `safety`, `osv-scanner`) as a CI step; fail the build on high/critical vulnerabilities.
- [ ] Add container image scanning (e.g., Trivy) as a CI step on built images.
- [ ] Write GitHub Actions workflow `cd.yml`: on merge to `main` — build, tag with semantic version (based on conventional commits), push images to a container registry (GHCR).
- [ ] Set up GitHub branch protection: required status checks (lint, tests, build) before merge; require PR review.
- [ ] Write a minimal Terraform config (`infra/terraform/`) provisioning a managed Postgres instance and a container registry on a real or simulated cloud provider (or LocalStack for practice).
- [ ] Write an Ansible playbook (or document the Terraform-only path if skipping Ansible) for configuring a target VM (or document why this step is skipped in favor of Kubernetes next sprint).
- [ ] Store all secrets (`DATABASE_URL`, `JWT_SECRET`, registry credentials) as GitHub Actions secrets — audit the repo to confirm none are committed.
- [ ] Document and practice a Git workflow: Trunk-Based Development with short-lived feature branches, squash-merge on PR, semantic commit messages driving automatic SemVer bumps.

### Testing Tasks
- [ ] Add a coverage threshold gate in CI (fail build if total coverage drops below the current baseline, e.g., 80%).
- [ ] Add a "flaky test" retry policy (max 1 retry) and track/flag any test that needs it for follow-up.
- [ ] Write a smoke-test script run post-build against the built Docker images (not just source) to catch "works on my machine, breaks in the image" issues.

### Architecture Improvements
- [ ] `docs/devops/pipeline.md` documenting the full CI/CD flow with a diagram (PR → checks → merge → build → scan → push → [deploy in Sprint 13]).
- [ ] `docs/devops/rollback-procedure.md` — documented and once actually rehearsed (revert a merge, confirm CI/CD re-deploys the previous good state).

### Expected Deliverables
- [ ] Every PR shows green/red checks for lint, types, tests, coverage, security scan, and build.
- [ ] Documented image-size reduction from multi-stage builds (e.g., "742MB → 168MB per service").
- [ ] A merged PR results in a versioned, scanned image pushed to the registry with zero manual steps.
- [ ] A rehearsed rollback, documented with exact commands used.

---

## Sprint 13 — Kubernetes-Ready: Pods, Deployments, Helm & Autoscaling

### Business Features
- [ ] N/A (internal) — but: the platform can now handle traffic spikes automatically and recover from individual instance failures without user-visible downtime.

### Backend Tasks
- [ ] Implement graceful shutdown in every FastAPI service: catch `SIGTERM`, stop accepting new requests, finish in-flight requests (drain), then exit within Kubernetes's `terminationGracePeriodSeconds`.
- [ ] Ensure `/health` (liveness) checks only "is the process alive" (no external dependency checks) and `/ready` (readiness) checks "can this pod serve traffic" (DB connection, Kafka/broker reachability) — verify these are genuinely different in behavior, not just name.
- [ ] Externalize all configuration (DB URLs, broker URLs, secrets) to environment variables sourced from ConfigMaps/Secrets — audit for any remaining hardcoded config.

### Frontend Tasks
- [ ] Build the frontend production bundle to be served via an Ingress-routed static host (or a small Nginx container serving the built assets).
- [ ] Inject environment-specific API base URLs at build/deploy time via a runtime config file (not baked into the JS bundle) so the same image works across environments.

### Database Changes
- [ ] Decide and document: managed/external Postgres per environment (recommended) vs a Kubernetes `StatefulSet` for local/dev cluster use — implement the `StatefulSet` version for local `kind`/`minikube` learning purposes regardless.
- [ ] Ensure the Sprint-12 CI migration step also runs as a Kubernetes `Job` (pre-deploy hook) in the cluster context.

### DevOps & Infrastructure Tasks
- [ ] Install a local Kubernetes cluster (`kind` or `minikube`).
- [ ] Write raw Kubernetes manifests first (`Deployment`, `Service`, `ConfigMap`, `Secret`) for one service to understand the primitives, then convert to a Helm chart.
- [ ] Build Helm charts (`helm create`) for every service (`api-gateway`, `catalog-service`, `payment-service`, `order-service`, `search-indexer`, `celery-worker`), parameterized via `values.yaml` per environment (dev/staging/prod).
- [ ] Configure liveness and readiness probes correctly and distinctly for every Deployment.
- [ ] Configure resource `requests`/`limits` for every container based on observed usage from earlier load tests.
- [ ] Configure a `HorizontalPodAutoscaler` for `api-gateway` and `catalog-service` based on CPU (and/or custom metrics later) with min/max replica bounds.
- [ ] Convert the nightly recommendation job (Sprint 10) into a Kubernetes `CronJob`.
- [ ] Configure `Ingress` (e.g., via `nginx-ingress` controller) routing external traffic to `api-gateway` and the frontend static service, with a `Namespace` per environment.
- [ ] Store secrets via Kubernetes `Secret` objects (documented limitation: not encrypted at rest by default; note Sealed Secrets/External Secrets as the production-grade follow-up).
- [ ] Add `helm lint` and a manifest-validation step (e.g., `kubeval`/`kubeconform`) to CI.
- [ ] Extend the GitHub Actions `cd.yml` from Sprint 12 to run `helm upgrade --install` against the local/test cluster after image push.

### Testing Tasks
- [ ] Smoke test suite run automatically against the cluster post-deploy (hits `/health`, `/ready`, and 3–4 critical endpoints).
- [ ] Load test (re-run the Sprint 4/5/7 Locust scripts) against the clustered deployment; observe and record HPA scaling pod count up and back down.
- [ ] Chaos-lite test: `kubectl delete pod <catalog-pod>` mid-load-test; assert zero dropped requests due to graceful shutdown + readiness gating + replica count > 1.
- [ ] Test rolling update: deploy a new image version while under load; assert no downtime and requests are served throughout.

### Architecture Improvements
- [ ] `docs/architecture/kubernetes-topology.md` documenting Namespaces, Deployments, Services, Ingress routing, and the CronJob.
- [ ] ADR: "Managed Postgres vs self-hosted StatefulSet in Kubernetes — decision and trade-offs for this project."

### Expected Deliverables
- [ ] `helm install atlascommerce ./charts` brings up the entire system on a local cluster in one command.
- [ ] Documented HPA behavior under load (screenshots/logs of replica count scaling up and down).
- [ ] Zero-downtime rolling update demonstrated and documented.
- [ ] Zero dropped requests during a live pod-kill test.

---

## Sprint 14 — Full Observability: Metrics, Logs, Traces & SLOs

### Business Features
- [ ] N/A (internal) — but: engineers can now detect and diagnose a production problem (e.g., a slow checkout) within minutes using dashboards, without reading code or SSHing into a server.

### Backend Tasks
- [ ] Add `prometheus-fastapi-instrumentator` (or manual `prometheus_client` middleware) to every service exposing `/metrics` with RED metrics (Rate, Errors, Duration) per endpoint.
- [ ] Add OpenTelemetry SDK + auto-instrumentation (FastAPI, SQLAlchemy, `httpx`, gRPC, Kafka client) to every service; configure the OTLP exporter pointing to a local collector.
- [ ] Add manual spans around business-critical operations (checkout, saga steps, search queries) with meaningful span names and attributes (e.g., `order.id`, `variant.id`).
- [ ] Ensure structured JSON logging includes `trace_id`/`span_id` in every log line (correlating logs ↔ traces).
- [ ] Configure Sentry SDK in every backend service for exception tracking, with PII/secret scrubbing rules configured (strip `Authorization` headers, password fields, etc.).
- [ ] Add a `/metrics`-based custom metric for the Sprint-9 saga: count of orders currently in each state, saga step duration histograms.

### Frontend Tasks
- [ ] Integrate Sentry frontend SDK for JS error tracking and basic performance/RUM (page load, route-change timings).
- [ ] Ensure the frontend also propagates a trace/correlation ID header on API calls so a user's click can be traced end-to-end into the backend.

### Database Changes
- [ ] No schema changes — verify SQLAlchemy OTel instrumentation correctly emits a span per query (spot-check against the Sprint-4 N+1 scenario reproduced deliberately).

### DevOps & Infrastructure Tasks
- [ ] Add `prometheus`, `grafana`, `loki` + `promtail` (or equivalent log shipper), `jaeger`, and an `otel-collector` to `docker-compose.yml` (and later Helm charts for the cluster).
- [ ] Write Prometheus scrape configs targeting every service's `/metrics`.
- [ ] Build Grafana dashboards (provisioned as JSON, checked into the repo) for: (a) per-service RED metrics, (b) saga/order-state metrics, (c) cache hit ratio (from Sprint 7), (d) Kafka consumer lag (from Sprint 9).
- [ ] Configure Loki log aggregation across all services with label-based filtering (service name, environment).
- [ ] Configure Alertmanager with rules based on SLO burn rate (defined below), not raw thresholds — route alerts to a webhook/console for local demo purposes.
- [ ] Add Grafana + Prometheus + Loki + Jaeger to the Kubernetes Helm setup from Sprint 13 (as a monitoring namespace).

### Testing Tasks
- [ ] Synthetic monitoring script: a scheduled job that exercises the 3 critical journeys (browse → search → checkout) every N minutes and reports success/failure/latency to Prometheus (via a Pushgateway or a dedicated exporter).
- [ ] Test: deliberately reintroduce the Sprint-4 N+1 bug on a feature branch; verify it becomes visible on the Grafana dashboard (query count/duration spike) without reading any code — then revert.
- [ ] Test: trigger an unhandled exception in a service; verify it appears correctly in Sentry with a usable stack trace and no leaked secrets.
- [ ] Test: follow one checkout request's trace ID through Jaeger across Gateway → Order → Kafka → Inventory → Payment spans, confirming the full journey is visible in a single trace.

### Architecture Improvements
- [ ] Define and document SLIs/SLOs/SLAs formally in `docs/observability/slos.md` for 3 journeys: e.g., "Checkout success rate SLI, SLO 99.5% over 30 days"; "Search p95 latency SLI, SLO < 300ms."
- [ ] Introduce a shared observability middleware/library used by every service so new endpoints get RED metrics + tracing automatically, without each developer remembering to add it manually.

### Expected Deliverables
- [ ] Grafana dashboards live and screenshot-documented in the repo.
- [ ] A recorded (or documented) demo: reproduce the N+1 bug, see it on the dashboard within minutes.
- [ ] A single Jaeger trace screenshot showing a full cross-service checkout request.
- [ ] `docs/observability/slos.md` finalized.

---

## Sprint 15 — Resilience, Chaos, Load Testing & Interview Readiness

### Business Features
- [ ] If the Payment service becomes slow or unavailable, the rest of the platform (browsing, cart) remains fully usable, and in-flight orders are safely compensated rather than left in a broken state.
- [ ] Non-critical features (recommendations, reviews) degrade gracefully without blocking core shopping/checkout flows.

### Backend Tasks
- [ ] Implement a Circuit Breaker (e.g., using `pybreaker` or a hand-rolled state machine: closed/open/half-open) around the Gateway's gRPC calls to `payment-service` and `catalog-service`.
- [ ] Define explicit fallback behavior for each circuit-broken call (e.g., catalog call open → serve last-cached product data with a `degraded` flag; payment call open → reject checkout immediately with a clear "try again shortly" message instead of hanging).
- [ ] Implement the Bulkhead Pattern: give each downstream dependency (Payment, Catalog, Search) its own bounded connection pool/semaphore in the Gateway so a slow one can't exhaust resources needed for the others.
- [ ] Standardize Retry Policy with jitter (e.g., `tenacity` library) across all inter-service calls; tune per-call timeouts (`connect_timeout`, `read_timeout`, `write_timeout`) explicitly rather than relying on defaults.
- [ ] Implement a simple Feature Flag system (e.g., a `feature_flags` table or config service) and wrap at least one risky feature (e.g., recommendations) behind a flag that can be toggled without a redeploy.
- [ ] Implement graceful degradation for the recommendations widget and reviews section: if their backing services/queries fail or time out, the page still renders the core product info.

### Frontend Tasks
- [ ] Add fallback/skeleton UI states for the recommendation carousel and review section when their data fails to load.
- [ ] Add a global "degraded mode" banner driven by the Gateway's `degraded` response flag.

### Database Changes
- [ ] Configure a read replica for Postgres locally (or simulate via a second Postgres instance with logical/streaming replication) for the failover drill.
- [ ] Add a `feature_flags` table (`key`, `enabled`, `description`) if not using an external config service.

### DevOps & Infrastructure Tasks
- [ ] Write a chaos script (`scripts/chaos_kill_pod.sh`) that randomly kills a pod (Payment or Catalog) in the Kubernetes cluster at intervals during a load test.
- [ ] Run the full Sprint-13 Locust load test **while** the chaos script is active; capture Grafana/Jaeger screenshots during the incident.
- [ ] Perform a database failover drill: stop the primary Postgres instance, promote the replica, measure and record RTO (recovery time objective) and RPO (recovery point objective, i.e., how much data if any was lost).
- [ ] Run the full OWASP Top 10 review across the system: verify/test mitigations for SQL Injection (parameterized queries via ORM — confirm no raw string interpolation anywhere), XSS (React's default escaping + CSP headers), CSRF (SameSite cookies / token-based auth), CORS (explicit allow-list, not `*`), SSRF (validate/allow-list any server-side outbound URL fetches, e.g., webhook URLs), XXE (confirm XML parsing, if any, disables external entities), Clickjacking (`X-Frame-Options`/CSP `frame-ancestors`).
- [ ] Run a final dependency + container image vulnerability scan across all services and remediate/document any findings.

### Testing Tasks
- [ ] Chaos test: assert the circuit breaker opens correctly when Payment is killed, the Gateway returns fast, clear errors (not hangs/timeouts) for new checkout attempts, and existing in-flight sagas compensate correctly.
- [ ] Load + chaos combined test: system-wide error rate stays within the SLO error budget defined in Sprint 14 despite the induced failure (or, if it doesn't, document why and what you'd change).
- [ ] Failover drill test: application automatically reconnects to the promoted replica without a manual restart (or document the manual steps required, if full automation is out of scope).
- [ ] Full test-pyramid audit: generate and review a coverage report across Unit/Integration/Functional/E2E tests for every service; identify and fill any critical gaps.
- [ ] Security test pass: run automated tools (e.g., `bandit` for Python, `zap-baseline` or similar for a basic dynamic scan) and manually verify each OWASP item above with a concrete test or proof.

### Architecture Improvements
- [ ] Write Architecture Decision Records (ADRs) for the 10 most significant decisions made across all 15 sprints (e.g., orchestration vs choreography sagas, pessimistic vs optimistic locking, database-per-service, Outbox Pattern, CQRS read model, Kubernetes StatefulSet vs managed DB).
- [ ] Write a formal incident postmortem for the chaos-drill "incident," following a blameless postmortem template (timeline, impact, root cause, action items).

### Expected Deliverables
- [ ] `docs/incidents/chaos-drill-postmortem.md` with real Grafana/Jaeger evidence.
- [ ] `docs/architecture/adrs/` folder with 10 ADRs.
- [ ] `docs/security/owasp-top-10-review.md` mapping each OWASP item to its implemented mitigation and test proof.
- [ ] A final, portfolio-ready `README.md`: architecture diagram, tech stack rationale, key trade-offs, and links to all the docs produced across the roadmap.
- [ ] A rehearsed 10-minute verbal walkthrough of the entire AtlasCommerce architecture, ready for system-design interviews.
