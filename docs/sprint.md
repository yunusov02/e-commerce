# Production E-Commerce Backend Roadmap

## 1. Overall Learning Strategy

This roadmap builds a production-grade e-commerce platform over 15 cumulative sprints. FastAPI is the primary backend framework, PostgreSQL is the main transactional database, and React with TypeScript is the frontend. Django, Django REST Framework, and Flask are introduced through focused comparison modules so you learn their patterns without splitting the main project into too many directions.

The sequence moves from a clean modular monolith to production-like distributed components:

- Sprints 1-4: backend fundamentals, project structure, PostgreSQL modeling, authentication, catalog, and API design.
- Sprints 5-8: cart, checkout, orders, payments, background jobs, Redis, Celery, RabbitMQ, and reliability basics.
- Sprints 9-11: search, MongoDB, Kafka, event-driven workflows, admin/internal tools, and cross-framework comparison with Django/DRF and Flask.
- Sprints 12-15: observability, security hardening, Kubernetes, CI/CD, performance, resilience, and final portfolio polish.

By the end, the project should show middle+ backend ability: clear architecture, correct data modeling, reliable async processing, strong tests, production deployment knowledge, observability, and the ability to discuss tradeoffs in interviews.

## 2. High-Level System Architecture

The final system should be a modular monolith with selected service-like boundaries. FastAPI remains the main API application. Some components are separated by process or infrastructure, but the project avoids premature microservices until there is a real reason.

### Target Components

- FastAPI application: main customer API for auth, users, catalog, cart, checkout, orders, reviews, inventory, and admin-facing endpoints.
- PostgreSQL: source of truth for users, products, categories, inventory, carts, orders, payments, coupons, reviews, and audit-friendly transactional data.
- Redis: caching, rate limiting, sessions or token denylist, cart acceleration where appropriate, distributed locks for inventory reservations.
- Celery workers: background jobs such as email notifications, image processing, order expiration, payment reconciliation, and scheduled cleanup.
- RabbitMQ: task queue broker for Celery and command-style background workflows.
- Kafka: event stream for domain events such as `OrderCreated`, `PaymentSucceeded`, `InventoryReserved`, `ProductViewed`, and analytics/search projections.
- MongoDB: flexible document storage for product view events, user activity snapshots, denormalized analytics, or audit/event documents where schema flexibility is useful.
- Elasticsearch or OpenSearch: product search, filtering, faceting, autocomplete, relevance tuning, and search projections from product events.
- S3 or MinIO: product images, user-uploaded files, invoices, exports, and generated assets.
- Nginx: reverse proxy, static asset routing, TLS termination in production-like setup.
- ASGI: FastAPI served by Uvicorn or Gunicorn with Uvicorn workers.
- WSGI: Django/DRF and Flask comparison modules deployed with WSGI servers where appropriate.
- React and TypeScript: customer storefront plus basic admin/internal screens.
- Prometheus and Grafana: metrics collection and dashboards.
- Loki: centralized logs.
- OpenTelemetry: traces across API, database, cache, queues, and workers.
- Sentry: error reporting and release-aware exception tracking.
- Docker Compose: local development environment.
- Kubernetes: later deployment target for production-like orchestration.
- CI/CD: linting, typing, tests, builds, migrations, images, and deployment pipeline.

### Architectural Shape

- Core commerce backend: modular monolith in FastAPI.
- Worker layer: separate Celery worker processes using the same domain code where practical.
- Search indexing: service-like projection pipeline using Kafka or queue consumers.
- Admin/internal tools: mostly FastAPI admin endpoints plus a small Django/DRF comparison implementation.
- Flask module: small service-style webhook receiver or health/status API to compare Flask's lightweight model with FastAPI.

The main lesson is not "microservices everywhere." The lesson is learning where boundaries help: data ownership, scaling, failure isolation, async workflows, search projections, and operational visibility.

## 3. 15-Sprint Roadmap

## Sprint 1: Project Foundation and Local Development

### Goal

Create the project foundation: FastAPI backend skeleton, React TypeScript frontend, PostgreSQL, Docker Compose, basic health checks, configuration, and first tests.

### Topics To Learn

- FastAPI routing, request/response lifecycle, app startup, dependency injection basics.
- Pydantic schemas and validation.
- Python project structure, virtual environments, dependency management, formatting, linting.
- Docker, Docker Compose, environment variables, local service networking.
- PostgreSQL basics: tables, primary keys, foreign keys, indexes, migrations.
- pytest fundamentals and test organization.
- ASGI basics and how FastAPI runs.

### Why It Matters

Production systems need repeatable local setup, clear project structure, and early testing. Without this, every later feature becomes harder to reason about.

### What To Build

- FastAPI app with `/health`, `/ready`, `/api/v1/status`.
- React TypeScript app with a simple status page that calls the backend.
- PostgreSQL connected through SQLAlchemy or SQLModel.
- Alembic migrations.
- Docker Compose for backend, frontend, PostgreSQL, and optional pgAdmin.
- Basic CI workflow for linting and tests.

### Technical Tasks

- Create backend package layout: `app/api`, `app/core`, `app/db`, `app/models`, `app/schemas`, `app/services`, `app/repositories`, `app/tests`.
- Add settings management with Pydantic settings.
- Add database session dependency.
- Add first migration for a simple `app_metadata` or `health_checks` table.
- Add global exception response format.
- Add OpenAPI metadata and API version prefix.

### Frontend Tasks

- Initialize React with TypeScript.
- Add API client wrapper.
- Build status page showing backend health and app version.
- Add basic error and loading states.

### Database Design Tasks

- Define naming conventions for tables, constraints, indexes, and migrations.
- Practice `CREATE TABLE`, `ALTER TABLE`, `EXPLAIN`, and simple indexes.
- Document migration workflow.

### Async / Background / Messaging Tasks

- Learn FastAPI `async def` vs normal `def`.
- Do not add Celery yet; document where background jobs will be introduced later.

### DevOps / Infrastructure Tasks

- Dockerfile for backend.
- Dockerfile or dev server setup for frontend.
- Docker Compose network and volumes.
- `.env.example`.
- Makefile or task runner commands for test, lint, format, migrate, and dev.

### Observability Tasks

- Structured JSON logs for backend.
- Request ID middleware.
- Basic health and readiness endpoints.

### Testing Tasks

- pytest setup.
- FastAPI `TestClient` or `httpx.AsyncClient`.
- Unit test health endpoints.
- Integration test database connection.
- Frontend component smoke test if tooling is available.

### Deliverables

- Running local stack with one command.
- Backend API docs available.
- Frontend can call backend.
- First migration applied.
- CI checks passing.

### Definition Of Done

- `docker compose up` starts the system.
- Tests pass locally.
- Migrations run from empty database.
- README explains local setup.
- Health endpoints return stable JSON.

### Pitfalls

- Hardcoding settings instead of using environment variables.
- Mixing database models, schemas, and route logic in one file.
- Skipping migrations and manually changing the database.
- Treating Docker as a final production setup too early.

### Interview Readiness

- Explain ASGI and why FastAPI uses it.
- Explain dependency injection in FastAPI.
- Explain why migrations matter.
- Explain Docker Compose networking.
- Explain the difference between unit and integration tests.

## Sprint 2: Users, Authentication, Authorization, and Security Basics

### Goal

Implement user registration, login, JWT authentication, password hashing, roles, permissions, and protected endpoints.

### Topics To Learn

- Authentication vs authorization.
- Password hashing with bcrypt or Argon2.
- JWT access tokens, refresh tokens, expiry, rotation, and revocation tradeoffs.
- FastAPI security dependencies.
- Pydantic validation for sensitive inputs.
- SQL constraints for uniqueness and integrity.
- Basic security: CORS, rate limiting concepts, secrets handling.

### Why It Matters

Every e-commerce system handles user identity, personal data, and protected operations. Weak auth design causes serious production risk.

### What To Build

- User registration and login.
- Refresh token flow.
- Current user endpoint.
- Role-based access: customer, staff, admin.
- User profile read/update.
- Password change.

### Technical Tasks

- Add `users`, `roles`, `user_roles`, and `refresh_tokens` tables.
- Implement password hashing service.
- Implement auth dependencies: `get_current_user`, `require_admin`, `require_staff`.
- Add consistent 401/403 errors.
- Add token denylist strategy using database now, Redis later.
- Add email uniqueness validation.

### Frontend Tasks

- Registration page.
- Login page.
- Auth state management.
- Protected route handling.
- Profile page.

### Database Design Tasks

- Model one-to-many and many-to-many relationships.
- Add unique indexes on email and username if used.
- Add timestamps: `created_at`, `updated_at`, `last_login_at`.
- Discuss soft delete vs hard delete for users.

### Async / Background / Messaging Tasks

- Use FastAPI background tasks only for simple local development email logging.
- Document why real email delivery will move to Celery later.

### DevOps / Infrastructure Tasks

- Add secure secret settings.
- Add CORS configuration.
- Add local SMTP test service only if useful.

### Observability Tasks

- Log authentication failures safely without logging passwords or tokens.
- Add request ID to auth logs.
- Add basic auth-related metrics placeholder.

### Testing Tasks

- Unit tests for password hashing and token creation.
- Integration tests for registration, login, refresh, protected endpoints.
- Negative tests for invalid token, expired token, wrong password, duplicate email.
- Security tests for password not returned in API responses.

### Deliverables

- Working auth flow from frontend to backend.
- Protected profile endpoint.
- Role-based admin-only endpoint.
- Auth tests.

### Definition Of Done

- Passwords are hashed, never stored or returned.
- JWT expiry is enforced.
- Protected endpoints reject anonymous users.
- Admin endpoints reject normal users.
- Tests cover happy path and failure path.

### Pitfalls

- Storing plain text passwords.
- Putting secrets in Git.
- Returning too much user data.
- Confusing authentication with authorization.
- Making refresh tokens impossible to revoke.

### Interview Readiness

- Explain JWT pros and cons.
- Explain password hashing vs encryption.
- Explain 401 vs 403.
- Explain role-based access control.
- Explain common auth vulnerabilities.

## Sprint 3: Product Catalog, Categories, Attributes, and Files

### Goal

Build the product catalog with categories, product attributes, images, and admin CRUD.

### Topics To Learn

- REST API design for resources.
- Pagination, filtering, and sorting.
- PostgreSQL relationships and indexes.
- Flexible product attributes: relational tables vs JSONB.
- File uploads in FastAPI.
- S3/MinIO object storage concepts.
- OpenAPI documentation quality.

### Why It Matters

Catalog modeling is central to e-commerce. Poor modeling makes search, filtering, inventory, and admin workflows painful.

### What To Build

- Product CRUD.
- Category tree or parent-child categories.
- Product attributes such as color, size, brand, material.
- Product image upload to MinIO.
- Public product listing and detail endpoints.
- Staff/admin product management screens.

### Technical Tasks

- Add models: `products`, `categories`, `product_images`, `attributes`, `attribute_values`, `product_attribute_values`.
- Implement API versioned routes under `/api/v1/catalog`.
- Add pagination with limit/offset or cursor strategy.
- Add filtering by category, price range, status, brand, attributes.
- Add sorting by price, newest, popularity placeholder.
- Add file upload validation: type, size, extension.
- Store file metadata in PostgreSQL and binary objects in MinIO.

### Frontend Tasks

- Product listing page.
- Product detail page.
- Admin product form.
- Category navigation.
- Image upload UI.
- Loading, empty, and error states.

### Database Design Tasks

- Compare normalized attributes vs JSONB.
- Add indexes for category, status, slug, price.
- Add slug uniqueness.
- Add constraints for product status.
- Learn query plans with `EXPLAIN ANALYZE`.

### Async / Background / Messaging Tasks

- Keep image processing synchronous only if small.
- Plan future background image resizing.

### DevOps / Infrastructure Tasks

- Add MinIO to Docker Compose.
- Add bucket initialization instructions.
- Add storage configuration.

### Observability Tasks

- Log upload failures with request ID.
- Add basic timing logs for catalog list endpoint.
- Track slow database queries manually during development.

### Testing Tasks

- Unit tests for product validation.
- Integration tests for product CRUD and filtering.
- File upload tests.
- Database constraint tests.
- Frontend tests for catalog rendering.

### Deliverables

- Browsable product catalog.
- Admin product management.
- Image storage through MinIO.
- Documented API schema.

### Definition Of Done

- Products can be created, listed, filtered, viewed, updated, and archived.
- Images upload to object storage and display in frontend.
- Filtering queries are indexed or justified.
- Tests cover product API behavior.

### Pitfalls

- Storing image blobs directly in PostgreSQL.
- Designing attributes so rigidly that new categories require schema changes.
- Adding filters without indexes.
- Returning huge unpaginated product lists.

### Interview Readiness

- Explain object storage vs database storage.
- Explain pagination strategies.
- Explain normalized schema vs JSONB.
- Explain indexing for common product queries.
- Explain FastAPI file uploads.

## Sprint 4: Inventory Management and Domain Modeling

### Goal

Implement inventory tracking, stock reservations, SKU variants, and domain-level business rules.

### Topics To Learn

- Domain modeling and service layer design.
- Transactions and isolation levels.
- Race conditions in inventory systems.
- Optimistic vs pessimistic locking.
- Database constraints and invariants.
- Repository pattern tradeoffs.

### Why It Matters

Inventory is where correctness matters. Overselling products is one of the classic failures in commerce systems.

### What To Build

- SKU variants for products.
- Inventory records.
- Stock adjustment workflow.
- Reservation model for checkout preparation.
- Admin inventory adjustment screen.
- Audit log for stock changes.

### Technical Tasks

- Add models: `product_variants`, `inventory_items`, `inventory_reservations`, `stock_movements`.
- Implement inventory service methods: reserve, release, commit, adjust.
- Use database transactions around reservation changes.
- Add idempotency key support for stock operations.
- Add clear domain errors such as `InsufficientStock`.
- Add admin-only endpoints for manual adjustments.

### Frontend Tasks

- Variant selection on product detail page.
- Display stock state: in stock, low stock, out of stock.
- Admin inventory dashboard.
- Stock adjustment form.

### Database Design Tasks

- Add constraints preventing negative available stock.
- Add indexes for SKU, product variant, reservation expiry.
- Model audit-friendly append-only stock movements.
- Practice transaction behavior with concurrent tests.

### Async / Background / Messaging Tasks

- Add scheduled concept for reservation expiry, implemented later with Celery.
- For now, release expired reservations via manual endpoint or startup-safe management command.

### DevOps / Infrastructure Tasks

- Add database migration rollback practice.
- Seed sample inventory data.

### Observability Tasks

- Log all stock movement events.
- Add metrics placeholders for reservation success/failure.
- Add warning logs for low stock.

### Testing Tasks

- Unit tests for inventory service.
- Integration tests for reservation lifecycle.
- Concurrent reservation tests.
- Tests for negative stock prevention.

### Deliverables

- SKU-level inventory management.
- Stock reservation logic.
- Stock audit trail.
- Admin inventory UI.

### Definition Of Done

- Two concurrent checkouts cannot reserve the same final item incorrectly.
- Stock changes are auditable.
- Inventory operations are transactional.
- Tests prove insufficient stock behavior.

### Pitfalls

- Calculating stock only in application memory.
- Ignoring concurrent requests.
- Updating stock without audit records.
- Treating inventory as a simple integer field on product.

### Interview Readiness

- Explain transaction isolation.
- Explain race conditions and locking.
- Explain idempotency keys.
- Explain why inventory needs audit logs.
- Explain service layer responsibilities.

## Sprint 5: Cart, Checkout Preparation, and Redis

### Goal

Build cart functionality, checkout preparation, Redis caching, and Redis-backed rate limiting or token denylist.

### Topics To Learn

- Cart modeling: database-backed vs Redis-backed.
- Redis data structures and TTLs.
- Cache invalidation.
- Distributed locks basics.
- API idempotency for cart operations.
- FastAPI middleware for rate limiting.

### Why It Matters

Carts are high-traffic and change frequently. Redis helps reduce database load, but cache consistency must be designed carefully.

### What To Build

- Add to cart, update quantity, remove item.
- Persistent cart for logged-in users.
- Anonymous cart strategy using local storage and merge after login.
- Checkout preview with totals.
- Redis cache for product detail or catalog fragments.
- Redis token denylist or rate limit.

### Technical Tasks

- Add models: `carts`, `cart_items`.
- Implement cart service with clear price snapshot behavior.
- Add Redis client dependency.
- Cache product detail responses with TTL.
- Invalidate cache when product changes.
- Add rate limiting for login and checkout preview endpoints.
- Merge anonymous cart into user cart.

### Frontend Tasks

- Cart page.
- Cart drawer or cart count.
- Quantity controls.
- Checkout preview page.
- Anonymous cart storage and merge flow.

### Database Design Tasks

- Decide whether cart item stores current product price or computes live price.
- Add unique constraint on `(cart_id, variant_id)`.
- Index user cart lookup.
- Model cart state: active, checked_out, abandoned.

### Async / Background / Messaging Tasks

- No Celery yet, but define future cart-abandonment cleanup job.
- Use Redis TTL for selected temporary values.

### DevOps / Infrastructure Tasks

- Add Redis to Docker Compose.
- Add Redis health checks.
- Configure local Redis URL.

### Observability Tasks

- Log cache hits and misses at debug level.
- Track rate limit rejections.
- Add simple Redis availability health check.

### Testing Tasks

- Unit tests for cart merge logic.
- Integration tests for cart CRUD.
- Redis integration tests.
- Tests for cache invalidation.
- Tests for rate limit behavior.

### Deliverables

- Working cart from frontend.
- Redis integrated.
- Checkout preview.
- Cache and rate limit examples.

### Definition Of Done

- Logged-in users have persistent carts.
- Anonymous carts merge after login.
- Cart totals are correct.
- Redis failure mode is understood and documented.
- Tests cover cart edge cases.

### Pitfalls

- Trusting frontend prices.
- Forgetting to invalidate cached product data.
- Using Redis as the only source of truth for important order data.
- Making rate limits impossible to test.

### Interview Readiness

- Explain Redis use cases.
- Explain cache-aside pattern.
- Explain cache invalidation problems.
- Explain why checkout cannot trust client-side totals.
- Explain Redis TTL and data structures.

## Sprint 6: Orders, Checkout, Payments, and Idempotency

### Goal

Implement order creation, checkout flow, mock payment provider, payment state machine, and idempotent APIs.

### Topics To Learn

- Order lifecycle modeling.
- Payment state machines.
- Idempotency in distributed workflows.
- Transaction boundaries.
- Webhook design.
- Decimal money handling.
- API error design.

### Why It Matters

Checkout is the business-critical path. It must be correct, observable, idempotent, and resilient to retries.

### What To Build

- Checkout endpoint that converts cart to order.
- Order records with line items and price snapshots.
- Mock payment provider.
- Payment intent creation.
- Payment callback or webhook simulation.
- Order detail and order history pages.

### Technical Tasks

- Add models: `orders`, `order_items`, `payments`, `payment_events`, `idempotency_keys`.
- Implement order state: pending, paid, processing, shipped, canceled, refunded.
- Implement payment state: requires_payment, processing, succeeded, failed, refunded.
- Use `Decimal` for money.
- Add idempotency key middleware or dependency for checkout/payment endpoints.
- Validate inventory reservation before order creation.
- Commit inventory only after successful payment or define chosen strategy clearly.

### Frontend Tasks

- Checkout form.
- Order confirmation page.
- Order history page.
- Payment success/failure UI.

### Database Design Tasks

- Store price snapshots on order items.
- Add indexes for user order history and payment provider references.
- Add unique idempotency key constraints.
- Add status constraints.

### Async / Background / Messaging Tasks

- Still mostly synchronous.
- Define events that will later become queue messages: `OrderCreated`, `PaymentSucceeded`, `PaymentFailed`.

### DevOps / Infrastructure Tasks

- Add seed script for test checkout data.
- Add local webhook simulation command.

### Observability Tasks

- Log checkout steps with correlation/request ID.
- Add metrics placeholders for payment success/failure.
- Add structured error logging for payment failures.

### Testing Tasks

- Unit tests for order total calculation.
- Integration tests for checkout success and failure.
- Idempotency tests with repeated requests.
- Payment webhook tests.
- Inventory commit/release tests.

### Deliverables

- End-to-end cart to order to payment flow.
- Mock payment provider.
- Order history.
- Idempotency tests.

### Definition Of Done

- Duplicate checkout requests do not create duplicate orders.
- Order item prices remain stable after product price changes.
- Payment states transition legally.
- Failed payments release or preserve inventory according to documented rules.

### Pitfalls

- Using floats for money.
- Creating duplicate orders on retry.
- Allowing impossible status transitions.
- Treating payment webhooks as trusted without verification concept.

### Interview Readiness

- Explain idempotency.
- Explain payment webhook risks.
- Explain order and payment state machines.
- Explain why order line items need price snapshots.
- Explain transaction boundaries in checkout.

## Sprint 7: Celery, RabbitMQ, Notifications, and Scheduled Jobs

### Goal

Introduce Celery with RabbitMQ for background processing, email notifications, image processing, reservation expiry, and scheduled jobs.

### Topics To Learn

- Message queues vs background tasks.
- Celery workers, tasks, retries, timeouts, dead letters.
- RabbitMQ exchanges, queues, acknowledgements, prefetch.
- At-least-once delivery.
- Idempotent consumers.
- Scheduled tasks with Celery Beat.

### Why It Matters

Production systems must move slow or unreliable work out of request paths. Queue processing introduces failure modes that middle+ engineers must understand.

### What To Build

- Email notification tasks.
- Order confirmation email.
- Payment failure email.
- Product image resizing task.
- Expired reservation cleanup task.
- Abandoned cart reminder prototype.

### Technical Tasks

- Add Celery app configuration.
- Add RabbitMQ to Docker Compose.
- Add worker and beat services.
- Convert local email logging to Celery tasks.
- Add task retry policies.
- Add idempotency to notification tasks.
- Add task status logging.
- Add image derivative generation and store outputs in MinIO.

### Frontend Tasks

- Notification preferences page.
- Show order email status if useful for admin.
- Display resized images from generated variants.

### Database Design Tasks

- Add `notifications`, `notification_deliveries`, or `email_outbox`.
- Add reservation expiry fields and indexes.
- Add image derivative metadata.

### Async / Background / Messaging Tasks

- Use Celery for notifications, image processing, reservation cleanup.
- Use RabbitMQ as broker.
- Practice retries and task failure.
- Implement outbox-style table for reliable task creation if ready.

### DevOps / Infrastructure Tasks

- Add worker and beat containers.
- Add RabbitMQ management UI locally.
- Add worker health checks.
- Add separate environment variables for workers.

### Observability Tasks

- Add task logs with task ID and correlation ID.
- Add metrics for task success, failure, retry.
- Add basic worker dashboard or Flower if desired.

### Testing Tasks

- Unit tests for task payload builders.
- Integration tests for reservation cleanup.
- Celery eager-mode tests.
- Tests for idempotent notification delivery.

### Deliverables

- Celery/RabbitMQ running locally.
- Real background jobs.
- Scheduled cleanup job.
- Notification records.

### Definition Of Done

- Slow work is not done inside HTTP request handlers.
- Failed tasks retry safely.
- Duplicate task execution does not duplicate important side effects.
- Expired reservations are cleaned automatically.

### Pitfalls

- Passing huge objects to Celery instead of IDs.
- Writing non-idempotent tasks.
- Ignoring task retry behavior.
- Assuming queues provide exactly-once processing.

### Interview Readiness

- Explain RabbitMQ acknowledgements.
- Explain at-least-once delivery.
- Explain Celery retry behavior.
- Explain idempotent consumers.
- Explain when not to use background jobs.

## Sprint 8: Discounts, Coupons, Pricing Rules, and Contract Tests

### Goal

Implement coupons, discounts, pricing rules, promotion validation, and contract tests for API behavior.

### Topics To Learn

- Pricing domain modeling.
- Rule validation and conflict handling.
- API contracts.
- Consumer-driven testing basics.
- Complex SQL queries and constraints.
- Clean service APIs.

### Why It Matters

Pricing bugs directly affect revenue and customer trust. Contract tests prevent breaking frontend or client integrations.

### What To Build

- Coupon creation and validation.
- Percentage and fixed-amount discounts.
- Minimum order amount.
- Usage limits per coupon and per user.
- Expiry dates.
- Coupon application in cart and checkout.
- Admin coupon UI.

### Technical Tasks

- Add models: `coupons`, `coupon_redemptions`, `pricing_adjustments`.
- Implement pricing service with deterministic calculation.
- Validate coupon eligibility.
- Record redemption on successful checkout.
- Prevent coupon overuse under concurrency.
- Add API contract tests for cart, checkout, and coupon endpoints.

### Frontend Tasks

- Coupon input on cart/checkout.
- Discount line item display.
- Admin coupon management screen.
- Clear error messages for invalid coupons.

### Database Design Tasks

- Add constraints for coupon code uniqueness.
- Add redemption indexes.
- Model pricing adjustments as order-level records.
- Practice partial indexes for active coupons if useful.

### Async / Background / Messaging Tasks

- Queue notification for coupon campaign email.
- Add scheduled task to deactivate expired campaigns if needed.

### DevOps / Infrastructure Tasks

- Add test fixtures for pricing scenarios.
- Add CI stage for contract tests.

### Observability Tasks

- Track coupon validation failure reasons.
- Log discount application decisions.
- Add metrics for coupon usage.

### Testing Tasks

- Unit tests for pricing service.
- Property-style tests for discount boundaries if possible.
- Integration tests for coupon redemption.
- Concurrency test for usage limits.
- Contract tests for API response shape.

### Deliverables

- Coupon system integrated into checkout.
- Pricing service with strong tests.
- Contract tests in CI.

### Definition Of Done

- Coupons cannot be overused.
- Order totals are reproducible from stored records.
- Invalid coupon errors are clear.
- Contract tests protect frontend-facing API shapes.

### Pitfalls

- Spreading pricing logic across routes.
- Applying discounts after payment incorrectly.
- Not recording how final price was calculated.
- Ignoring concurrency on usage limits.

### Interview Readiness

- Explain contract testing.
- Explain deterministic pricing.
- Explain concurrency risks in coupon usage.
- Explain where pricing logic should live.
- Explain partial indexes and constraints.

## Sprint 9: Reviews, Ratings, MongoDB, and Analytics Events

### Goal

Add reviews and ratings, introduce MongoDB for flexible event/activity documents, and build a simple analytics pipeline.

### Topics To Learn

- Relational vs document database tradeoffs.
- MongoDB document modeling.
- Event capture and activity streams.
- Aggregations and read models.
- Moderation workflows.
- Data consistency between PostgreSQL and MongoDB.

### Why It Matters

E-commerce platforms need user-generated content and analytics. MongoDB is useful when event shape changes often or when document-style reads are natural.

### What To Build

- Product reviews and ratings.
- Review moderation.
- Verified purchase checks.
- Product view events.
- Search/click activity documents in MongoDB.
- Basic analytics dashboard for product views and review stats.

### Technical Tasks

- Add PostgreSQL models: `reviews`, `review_votes`, `review_moderation_actions`.
- Add MongoDB collections: `product_events`, `user_activity_snapshots`.
- Implement review eligibility based on paid orders.
- Store event documents from product views and search clicks.
- Create analytics endpoints reading from MongoDB aggregations.
- Add moderation endpoints for staff.

### Frontend Tasks

- Review list and submission form.
- Rating summary component.
- Admin moderation queue.
- Simple analytics page.

### Database Design Tasks

- Keep authoritative reviews in PostgreSQL.
- Use MongoDB for flexible event payloads and analytics documents.
- Design indexes in MongoDB for product ID and event timestamp.
- Compare SQL aggregation vs MongoDB aggregation.

### Async / Background / Messaging Tasks

- Queue review notification to staff for flagged content.
- Queue analytics event writes if request latency becomes high.

### DevOps / Infrastructure Tasks

- Add MongoDB to Docker Compose.
- Add MongoDB init scripts or documented setup.
- Add local backup/restore practice.

### Observability Tasks

- Track review creation and moderation actions.
- Track event ingestion failures.
- Add logs around MongoDB availability.

### Testing Tasks

- Integration tests for review eligibility.
- MongoDB integration tests.
- Moderation workflow tests.
- Analytics aggregation tests.

### Deliverables

- Reviews and ratings live on product pages.
- MongoDB integrated for analytics/events.
- Moderation workflow.

### Definition Of Done

- Only eligible users can review purchased products.
- Review averages are correct.
- MongoDB use is justified and documented.
- Analytics endpoints work from event data.

### Pitfalls

- Using MongoDB just because it exists.
- Storing transactional order data in MongoDB without reason.
- Allowing duplicate reviews without rules.
- Forgetting moderation and abuse cases.

### Interview Readiness

- Explain PostgreSQL vs MongoDB tradeoffs.
- Explain document schema design.
- Explain eventual consistency.
- Explain review eligibility logic.
- Explain aggregation indexes.

## Sprint 10: Search With Elasticsearch/OpenSearch

### Goal

Implement production-like product search using Elasticsearch or OpenSearch, including indexing, filtering, faceting, autocomplete, and relevance tuning.

### Topics To Learn

- Search engine architecture.
- Inverted indexes.
- Full-text search vs SQL filtering.
- Analyzers, tokenizers, mappings.
- Facets and aggregations.
- Reindexing strategies.
- Search relevance and ranking.

### Why It Matters

Search is one of the highest-impact parts of e-commerce UX. It is also a common backend interview topic because it requires understanding indexing, consistency, and performance.

### What To Build

- Product indexing pipeline.
- Search endpoint.
- Category/attribute/price filters.
- Faceted counts.
- Autocomplete suggestions.
- Admin reindex command.
- Search UI.

### Technical Tasks

- Add OpenSearch or Elasticsearch to Docker Compose.
- Define product index mapping.
- Implement product indexing service.
- Index products after create/update/archive.
- Add bulk reindex command.
- Add search endpoint with query, filters, sorting, pagination.
- Add fallback behavior if search service is unavailable.

### Frontend Tasks

- Search bar.
- Search results page.
- Filters and facets.
- Autocomplete dropdown.
- Empty search state.

### Database Design Tasks

- Decide which fields are indexed from PostgreSQL.
- Track `search_index_version` or `indexed_at`.
- Compare source-of-truth data vs search projection.

### Async / Background / Messaging Tasks

- Use Celery task for indexing after product changes.
- Prepare for Kafka event-based indexing in next sprint.

### DevOps / Infrastructure Tasks

- Add search service health check.
- Add index initialization command.
- Add memory limits locally if needed.

### Observability Tasks

- Log search query latency.
- Track zero-result searches.
- Track indexing failures.
- Add basic search metrics.

### Testing Tasks

- Integration tests for indexing and search.
- Tests for filters and facets.
- Tests for reindex command.
- Contract tests for search response.

### Deliverables

- Search-backed product discovery.
- Search UI with filters.
- Reindex workflow.
- Documented mapping.

### Definition Of Done

- Product changes eventually appear in search.
- Search filters match catalog behavior.
- Reindexing can rebuild from PostgreSQL.
- Search failures do not crash unrelated APIs.

### Pitfalls

- Treating search index as source of truth.
- Forgetting reindex strategy.
- Building SQL-only search for complex relevance needs.
- Not measuring search latency.

### Interview Readiness

- Explain inverted indexes.
- Explain analyzers and mappings.
- Explain eventual consistency in search.
- Explain reindexing.
- Explain filters vs full-text query.

## Sprint 11: Kafka, Domain Events, Django/DRF, and Flask Comparisons

### Goal

Introduce Kafka for domain events and build small Django/DRF and Flask modules to compare framework styles against FastAPI.

### Topics To Learn

- Event-driven architecture.
- Kafka topics, partitions, offsets, consumer groups.
- Event schemas and versioning.
- Outbox pattern.
- FastAPI vs Django/DRF vs Flask.
- ORM differences and framework tradeoffs.

### Why It Matters

Middle+ backend engineers must know when to use events, how to avoid data loss, and how frameworks differ in real engineering tradeoffs.

### What To Build

- Domain event outbox in PostgreSQL.
- Kafka producer publishing events from outbox.
- Kafka consumer updating search or analytics projections.
- Django/DRF mini admin or reporting API.
- Flask mini webhook receiver or status service.
- Comparison notes in documentation.

### Technical Tasks

- Add models: `outbox_events`, `processed_events`.
- Emit events for order created, payment succeeded, product updated, review created.
- Add Kafka to Docker Compose.
- Add producer worker that reads outbox and publishes to Kafka.
- Add consumer for search indexing or MongoDB analytics projection.
- Add event schema version field.
- Create small Django project for reporting/admin comparison.
- Create small Flask app for webhook receiver comparison.

### Frontend Tasks

- Add admin/reporting page that calls the reporting API if useful.
- Keep main customer UX on FastAPI-backed APIs.

### Database Design Tasks

- Implement transactional outbox with PostgreSQL.
- Track processed Kafka events idempotently.
- Compare Django ORM models with SQLAlchemy models.

### Async / Background / Messaging Tasks

- Use Kafka for domain event stream.
- Keep RabbitMQ/Celery for task execution.
- Document RabbitMQ vs Kafka use cases.

### DevOps / Infrastructure Tasks

- Add Kafka and related UI if needed.
- Add Django and Flask container targets.
- Add local commands for consumers.

### Observability Tasks

- Track outbox lag.
- Track Kafka consumer lag.
- Log event IDs and correlation IDs.
- Add metrics for published and failed events.

### Testing Tasks

- Unit tests for event schema builders.
- Integration tests for outbox creation inside transactions.
- Consumer idempotency tests.
- Django/DRF endpoint tests.
- Flask endpoint tests.

### Deliverables

- Working Kafka event pipeline.
- Outbox pattern implemented.
- Django/DRF and Flask mini modules.
- Framework comparison document.

### Definition Of Done

- Events are not lost if a transaction commits.
- Consumers can process duplicate events safely.
- Kafka is used for event streams, RabbitMQ for tasks.
- You can explain FastAPI, Django/DRF, and Flask tradeoffs from code.

### Pitfalls

- Publishing events directly before database commit.
- Confusing Kafka with a task queue.
- Ignoring schema versioning.
- Building full duplicate apps in Django and Flask instead of focused comparisons.

### Interview Readiness

- Explain Kafka partitions and consumer groups.
- Explain outbox pattern.
- Explain RabbitMQ vs Kafka.
- Explain FastAPI vs Django/DRF vs Flask.
- Explain event versioning and idempotent consumers.

## Sprint 12: Admin Tools, Internal Operations, and WebSockets

### Goal

Build production-style admin/internal tools for order operations, inventory operations, support workflows, and real-time updates using WebSockets.

### Topics To Learn

- Internal tool design.
- Admin authorization.
- Audit logging.
- WebSockets in FastAPI.
- Real-time notifications.
- Operational workflows and support tooling.
- API versioning discipline.

### Why It Matters

Real commerce systems need staff workflows, not only customer endpoints. Admin actions require strong authorization, auditability, and clear operational UX.

### What To Build

- Admin dashboard.
- Order management: cancel, refund mock, mark shipped.
- Inventory adjustment workflows.
- Customer support user lookup.
- Audit log viewer.
- WebSocket notifications for order status changes or admin alerts.

### Technical Tasks

- Add admin route group.
- Add audit log model and service.
- Add WebSocket endpoint with authenticated connection.
- Add broadcast mechanism using Redis pub/sub if useful.
- Add explicit API versioning strategy.
- Add permission checks per admin action.
- Add staff action reason fields.

### Frontend Tasks

- Admin dashboard.
- Order management table.
- User detail support view.
- Audit log page.
- Live notification indicator via WebSocket.

### Database Design Tasks

- Add `audit_logs`, `admin_actions`, or domain-specific audit records.
- Index audit logs by actor, entity, and timestamp.
- Decide retention policy.

### Async / Background / Messaging Tasks

- Publish admin notifications through Redis pub/sub or task events.
- Queue export jobs for admin reports if useful.

### DevOps / Infrastructure Tasks

- Add admin environment flags.
- Add role seeding for staff/admin users.
- Add secure local test data.

### Observability Tasks

- Log every privileged action.
- Track WebSocket connections.
- Track admin error rates.
- Add audit log search.

### Testing Tasks

- Permission tests for every admin endpoint.
- WebSocket connection tests.
- Audit log tests.
- Admin workflow integration tests.

### Deliverables

- Functional internal admin tools.
- WebSocket real-time updates.
- Audit logging.

### Definition Of Done

- Admin actions are authorized and audited.
- Customer users cannot access staff endpoints.
- WebSocket updates work and fail gracefully.
- Support workflows are test-covered.

### Pitfalls

- Making admin endpoints less secure than public endpoints.
- Skipping audit logs for privileged actions.
- Letting WebSocket auth be weaker than HTTP auth.
- Building dashboards without actual operational workflows.

### Interview Readiness

- Explain WebSockets vs HTTP polling.
- Explain audit logging.
- Explain admin permission design.
- Explain API versioning.
- Explain operational tooling requirements.

## Sprint 13: Observability, Error Tracking, and Production Diagnostics

### Goal

Add serious observability: Prometheus metrics, Grafana dashboards, Loki logs, OpenTelemetry traces, and Sentry error tracking.

### Topics To Learn

- Metrics, logs, traces.
- RED and USE monitoring methods.
- OpenTelemetry instrumentation.
- Distributed tracing across API, database, Redis, Celery, and Kafka.
- Error reporting and release tracking.
- Alerting basics.

### Why It Matters

Production readiness means knowing what the system is doing, why it failed, and where latency comes from. Observability is a core middle+ skill.

### What To Build

- Metrics endpoint.
- Grafana dashboards.
- Loki log collection.
- OpenTelemetry traces.
- Sentry integration.
- Basic alerts for error rate, latency, worker failures, and queue lag.

### Technical Tasks

- Add Prometheus instrumentation to FastAPI.
- Instrument SQLAlchemy, Redis, Celery, and HTTP clients where possible.
- Add structured logs with correlation IDs across workers.
- Add OpenTelemetry exporter.
- Add Sentry SDK with environment and release tags.
- Add custom metrics for orders, payments, carts, search, queue jobs.

### Frontend Tasks

- Add frontend error boundary.
- Add basic frontend error reporting if desired.
- Add user-friendly error pages.

### Database Design Tasks

- Add optional operational tables for job status or imports if needed.
- Review slow query logging and indexes.

### Async / Background / Messaging Tasks

- Add Celery task metrics.
- Add Kafka consumer lag metrics.
- Add dead-letter or failed-task review process.

### DevOps / Infrastructure Tasks

- Add Prometheus, Grafana, Loki to Docker Compose.
- Add dashboards as code if possible.
- Add log scraping configuration.
- Add alert rule examples.

### Observability Tasks

- Build dashboards for API latency, error rate, throughput.
- Build dashboard for checkout funnel.
- Build dashboard for workers and queues.
- Build dashboard for database and Redis basics.

### Testing Tasks

- Test metrics endpoint exists.
- Test request ID propagation where feasible.
- Test Sentry is disabled or mocked in tests.
- Add smoke tests for observability stack config.

### Deliverables

- Working observability stack.
- Dashboards and example alerts.
- Traces visible for key flows.
- Sentry captures test error in local/dev mode.

### Definition Of Done

- You can debug a slow checkout using logs, metrics, and traces.
- Errors include request ID and release/environment.
- Worker failures are visible.
- Dashboards are documented.

### Pitfalls

- Logging sensitive data.
- Adding metrics without labels discipline.
- Creating high-cardinality metrics.
- Treating observability as only dashboards.

### Interview Readiness

- Explain logs vs metrics vs traces.
- Explain high-cardinality metric problems.
- Explain OpenTelemetry.
- Explain RED metrics.
- Explain how to debug production latency.

## Sprint 14: Kubernetes, CI/CD, Security Hardening, and Reliability

### Goal

Move toward production-like deployment with Kubernetes, stronger CI/CD, security hardening, reliability patterns, and deployment practices.

### Topics To Learn

- Kubernetes deployments, services, config maps, secrets, ingress.
- Nginx ingress/reverse proxy.
- CI/CD pipelines.
- Container image security.
- Secrets management.
- Blue-green or rolling deployments.
- Reliability: timeouts, retries, circuit breakers, graceful shutdown.
- OWASP API security.

### Why It Matters

A middle+ engineer should understand how code reaches production and how to reduce production risk.

### What To Build

- Kubernetes manifests or Helm chart.
- CI pipeline with lint, type check, tests, build.
- CD-style deployment to local cluster such as kind or minikube.
- Nginx ingress.
- Security headers and stricter CORS.
- Graceful shutdown for API and workers.
- Backup and restore scripts for PostgreSQL.

### Technical Tasks

- Add readiness and liveness probes.
- Configure Uvicorn/Gunicorn production settings.
- Add request timeouts.
- Add HTTP client timeout/retry policies.
- Add rate limiting for sensitive endpoints.
- Add dependency vulnerability scanning if practical.
- Add security review checklist.

### Frontend Tasks

- Build production frontend image.
- Configure frontend environment variables.
- Serve through Nginx or static hosting pattern.

### Database Design Tasks

- Add backup/restore documentation.
- Add migration deployment strategy.
- Review indexes and slow queries.

### Async / Background / Messaging Tasks

- Add graceful worker shutdown.
- Define retry and dead-letter policy.
- Document how workers deploy safely.

### DevOps / Infrastructure Tasks

- Add Kubernetes manifests for backend, frontend, PostgreSQL dependency strategy, Redis, workers, and ingress.
- Add GitHub Actions or similar CI.
- Build and tag Docker images.
- Add secrets/config separation.

### Observability Tasks

- Add Kubernetes-level metrics where practical.
- Ensure logs are still collected in cluster.
- Add deployment version labels to metrics and Sentry.

### Testing Tasks

- CI test suite.
- Container smoke tests.
- Migration smoke test from empty database.
- Basic end-to-end test in deployed environment.
- Security tests for headers and auth.

### Deliverables

- App deploys to local Kubernetes.
- CI pipeline passes.
- Security hardening checklist implemented.
- Backup/restore documented and tested.

### Definition Of Done

- Kubernetes deployment starts and passes readiness checks.
- CI blocks broken tests.
- Secrets are not committed.
- API handles shutdown gracefully.
- Basic production security controls exist.

### Pitfalls

- Treating Kubernetes as magic production readiness.
- Running migrations unsafely during deploys.
- Ignoring graceful shutdown.
- Storing secrets in manifests.
- Adding retries without timeouts.

### Interview Readiness

- Explain Kubernetes deployment vs service vs ingress.
- Explain readiness vs liveness probes.
- Explain rolling deployments.
- Explain graceful shutdown.
- Explain common API security risks.

## Sprint 15: Performance, Load Testing, Final Polish, and Portfolio Readiness

### Goal

Harden the system through performance testing, reliability review, documentation, final refactoring, and portfolio presentation.

### Topics To Learn

- Load testing and bottleneck analysis.
- Query optimization.
- Caching strategy review.
- Capacity planning basics.
- Architecture documentation.
- Code review discipline.
- Technical communication.
- Production readiness review.

### Why It Matters

The final sprint turns a feature-rich project into a professional portfolio artifact. The goal is to prove you can build, explain, test, operate, and improve a real backend system.

### What To Build

- Load test scenarios for browsing, search, cart, checkout.
- Performance dashboards.
- Final architecture docs.
- API documentation cleanup.
- Demo seed data.
- Portfolio README.
- Interview notes.
- Final bug fixes and refactors.

### Technical Tasks

- Run load tests with k6, Locust, or similar.
- Profile slow endpoints.
- Optimize selected database queries.
- Review indexes.
- Review Redis cache hit rates.
- Review Celery and Kafka lag under load.
- Add missing type hints.
- Improve error handling consistency.
- Remove dead code and duplicate abstractions.

### Frontend Tasks

- Polish customer storefront flows.
- Polish admin flows.
- Improve empty, loading, and error states.
- Add demo-friendly data and screenshots.

### Database Design Tasks

- Analyze slow query logs.
- Add or adjust indexes based on real query plans.
- Review migration history.
- Document data retention decisions.

### Async / Background / Messaging Tasks

- Load test queue-producing flows.
- Confirm task retries and idempotency.
- Test event consumers after restart.
- Document failure recovery steps.

### DevOps / Infrastructure Tasks

- Finalize CI/CD.
- Add deployment guide.
- Add environment matrix: local, test, staging-like.
- Add disaster recovery notes.

### Observability Tasks

- Use dashboards during load tests.
- Create final screenshots or exported dashboards.
- Document how to debug checkout, search, queue failure, and payment failure.

### Testing Tasks

- Full test suite review.
- Add missing high-value tests.
- Add end-to-end tests for critical flows.
- Add regression tests for discovered bugs.
- Run coverage report and improve meaningful gaps.

### Deliverables

- Production-style final project.
- Complete documentation.
- Load test report.
- Architecture diagrams.
- Portfolio README.
- Interview preparation notes.

### Definition Of Done

- Critical flows pass E2E tests.
- Load test results are documented.
- Observability can explain bottlenecks.
- README lets another engineer run the project.
- You can present architecture and tradeoffs confidently.

### Pitfalls

- Polishing UI while leaving backend correctness gaps.
- Optimizing without measurements.
- Hiding known limitations instead of documenting tradeoffs.
- Having features but no coherent story.

### Interview Readiness

- Explain the complete system architecture.
- Explain major tradeoffs and alternatives.
- Explain performance bottlenecks found and fixed.
- Explain how you would scale the system.
- Explain what you would improve next with more time.

## 4. Coverage Map

| Topic Group | Main Sprints | Practical Coverage |
|---|---:|---|
| Database and SQL | 1, 3, 4, 6, 8, 15 | PostgreSQL schema design, constraints, indexes, migrations, transactions, query plans, optimization |
| Distributed systems and backend | 6, 7, 10, 11, 14 | Idempotency, queues, Kafka, event-driven projections, retries, graceful shutdown |
| API and web | 1, 2, 3, 5, 6, 12 | REST, auth, pagination, filtering, error handling, WebSockets, versioning |
| Caching | 5, 10, 15 | Redis, cache-aside, invalidation, TTLs, search projection caching decisions |
| Message brokers and queues | 7, 11, 13, 15 | Celery, RabbitMQ, Kafka, task retries, consumer groups, lag monitoring |
| Architecture and design | 1, 4, 6, 8, 11, 15 | Modular monolith, service layer, domain events, outbox, tradeoff documentation |
| Python-specific | 1, 2, 4, 7, 15 | Packaging, typing, async/await, pytest, dependency management, clean services |
| FastAPI | 1-15 | Routing, DI, schemas, middleware, exceptions, auth, uploads, WebSockets, OpenAPI, testing, ASGI |
| Django / DRF / ORM | 11 | Mini reporting/admin API, Django ORM comparison, DRF serializers/viewsets |
| Flask | 11 | Mini webhook/status service, lightweight routing comparison |
| Testing | 1-15 | Unit, integration, contract, concurrency, E2E, observability smoke tests, load tests |
| Observability and production | 1, 7, 11, 13, 14, 15 | Logs, metrics, traces, Sentry, dashboards, alerts, debugging workflows |
| DevOps and deployment | 1, 3, 7, 11, 13, 14, 15 | Docker, Compose, MinIO, RabbitMQ, Kafka, Kubernetes, Nginx, CI/CD |
| Security | 2, 3, 5, 6, 12, 14 | Auth, RBAC, secrets, CORS, rate limiting, file validation, admin audit, OWASP |
| Performance and reliability | 4, 5, 6, 7, 10, 14, 15 | Locking, idempotency, cache, queues, search, retries, timeouts, load testing |
| Code review and communication | 8, 11, 14, 15 | Contract tests, framework comparison docs, security checklist, final architecture docs |

## 5. Final Outcome

By the end of the 15 sprints, you will have built a serious e-commerce platform with authentication, profiles, catalog, inventory, cart, checkout, payments, coupons, reviews, notifications, admin tools, search, caching, background jobs, event-driven communication, monitoring, CI/CD, containers, and Kubernetes deployment.

You should be comfortable working as a middle+ Python backend engineer because you will have practiced:

- Designing relational schemas and using PostgreSQL correctly.
- Building scalable FastAPI applications with clean structure.
- Writing reliable business logic around payments, orders, inventory, and pricing.
- Using Redis, Celery, RabbitMQ, Kafka, MongoDB, and OpenSearch for realistic reasons.
- Testing at multiple levels instead of only testing endpoints manually.
- Debugging production-style systems with logs, metrics, traces, and error reporting.
- Deploying and operating services with Docker, Nginx, Kubernetes, and CI/CD.
- Explaining architectural tradeoffs clearly.

In interviews, you should be able to confidently explain:

- How the request lifecycle works in FastAPI.
- How authentication, authorization, and token refresh work.
- How PostgreSQL transactions prevent inventory overselling.
- Why Redis is used for cache and rate limiting but not as the source of truth for orders.
- Why Celery/RabbitMQ and Kafka solve different problems.
- How the outbox pattern prevents lost events.
- How search indexing stays eventually consistent with PostgreSQL.
- How observability helps debug checkout or payment failures.
- How you would scale the system and what bottlenecks you would expect.
- How FastAPI compares with Django/DRF and Flask.

The strongest portfolio parts will be the checkout and inventory correctness, event-driven architecture, search implementation, observability dashboards, CI/CD pipeline, and clear architecture documentation. Those areas demonstrate that the project is more than CRUD and that you understand backend engineering as a production discipline.
