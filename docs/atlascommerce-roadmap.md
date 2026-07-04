# AtlasCommerce — The 15-Sprint Path to Middle+/Senior Python Backend Engineer

> A production-grade e-commerce platform used as the single vehicle to teach real backend engineering: architecture, distributed systems, databases, DevOps, and observability — through one continuously evolving codebase, not fifteen disconnected tutorials.

---

## 1. Overall Learning Strategy

**Core principle: feel the problem before you're handed the solution.**
Every sprint follows the same loop:

1. Build the feature the "naive" way first (or you already have a naive version from a previous sprint).
2. Run it under realistic load / realistic failure conditions until it breaks or misbehaves.
3. Diagnose *why* it broke using real tools (EXPLAIN, profilers, logs, tracing).
4. Learn the pattern/technology that exists specifically to solve that pain.
5. Refactor the code to production quality using that pattern.
6. Add tests + observability for the new behavior.
7. Document the trade-off you just made — nothing is free.

**Progression logic (Sprints 1 → 15):**

| Phase | Sprints | Architecture stage | Engineering focus |
|---|---|---|---|
| Foundations | 1–2 | Simple CRUD → Layered Architecture | Correctness, REST fundamentals, auth, clean layering |
| Core Domain | 3–6 | Modular Monolith → Production-ready Monolith | DDD, transactions, concurrency control, payments, idempotency |
| Scaling Up | 7–9 | Production Monolith → Distributed Architecture | Caching, async, background processing, event-driven design |
| Breaking Apart | 10–11 | Distributed → Microservice-ready | Search, polyglot persistence, service boundaries, gRPC |
| Shipping It | 12–13 | Microservice-ready → Kubernetes-ready | CI/CD, containers, orchestration |
| Hardening | 14–15 | Kubernetes-ready → Highly Observable Production System | Observability, resilience, chaos/load testing, interview mastery |

This is deliberately **not** "learn FastAPI, then learn Docker, then learn Kubernetes" in isolation. Every new tool is bolted onto the *same* growing codebase, so you experience integration pain — the thing tutorials never teach and interviews always ask about.

By Sprint 15 you will have rewritten major subsystems 3–4 times, which is intentional: production systems are refactored under load, not designed perfectly upfront (YAGNI in action).

---

## 2. Target System Architecture (End State — Post Sprint 15)

**Request flow (synchronous path):**
```
Client (React/TS) → Nginx (reverse proxy/TLS) → API Gateway
   → [Auth Service] (FastAPI) → [Catalog Service] (Django/DRF) → [Cart/Order Service] (Django/DRF) → [Payment Service] (FastAPI)
        Auth Service: FastAPI (ASGI/Uvicorn behind Gunicorn workers)
        Payment Service: FastAPI (ASGI/Uvicorn behind Gunicorn workers)
        Django services: Django/DRF (Gunicorn/uWSGI) with Repository → Service Layer → Domain (Hexagonal/Onion)
   → PostgreSQL (per-service schema/DB) | Redis (cache/session) | MongoDB (catalog docs, reviews)
```

**Event flow (asynchronous path):**
```
Order Service --(OrderCreated)--> Outbox table --(CDC/poller)--> Kafka topic "orders"
   --> Inventory Service (reserves stock) --> InventoryReserved / InventoryFailed
   --> Payment Service (charges) --> PaymentSucceeded / PaymentFailed
   --> Saga Orchestrator reacts to failures --> Compensation Transactions (release stock, refund)
   --> Notification Service (Celery worker via RabbitMQ) --> email/SMS
```

**Why each piece exists:**
- **Nginx**: TLS termination, reverse proxy, static file serving, first line of rate limiting.
- **FastAPI**: async-first, OpenAPI-native, type-safe — the primary API framework for the Auth Service and the API Gateway.
- **Django/DRF**: used for the Catalog, Order, Payment, and Admin/Internal Tools services once the monolith is split — especially where a batteries-included ORM/admin layer and rapid CRUD-heavy development are beneficial.
- **PostgreSQL**: ACID transactional core (orders, payments, inventory) — correctness matters more than raw throughput here.
- **MongoDB**: flexible schema for product catalog variants/attributes and review documents where rigid relational schema adds friction.
- **Redis**: cache-aside for hot reads, session store, distributed locks, rate limiting, Celery broker option.
- **RabbitMQ**: task queue for background jobs (emails, image processing) — reliable point-to-point/worker-queue semantics.
- **Kafka**: event backbone for cross-service domain events — durable, replayable, high-throughput pub/sub.
- **Elasticsearch/OpenSearch**: full-text product search, faceted filtering, relevance ranking.
- **MinIO/S3**: product images, invoices, static assets.
- **Docker/Kubernetes/Helm**: consistent packaging, orchestration, scaling, self-healing.
- **Prometheus/Grafana/Loki/OpenTelemetry/Jaeger/Sentry**: the "can you see production" layer — metrics, logs, traces, error tracking.
- **GitHub Actions**: CI (test/lint/build) + CD (deploy) automation.

**Data flow example (checkout):** Client submits cart → Order Service opens a DB transaction, writes an `Order` row plus an `OutboxEvent` row in the *same* transaction (Outbox Pattern, guaranteeing no lost events) → a relay publishes the event to Kafka → Inventory and Payment services consume asynchronously → a Saga tracks the multi-step workflow and triggers compensations on failure → the client polls or receives a WebSocket/SSE update.

---

## 3. The 15 Sprints

Each sprint below is intentionally dense — treat every bullet as a checklist item, not a paragraph to skim.

---

### Sprint 1 — Foundations: The Naive Product Catalog API

**Objective:** Ship a working CRUD API for Products/Categories with FastAPI + PostgreSQL, containerized, version-controlled — deliberately naive, to be refactored later.

**Why this sprint exists:** You cannot appreciate layered architecture, DI, or the Repository Pattern until you've written a monolithic `main.py` with SQL in your route handlers and felt it get unmanageable.

- **Backend concepts:** FastAPI routing, Pydantic models, path/query/body params, dependency injection basics, ASGI vs WSGI, Uvicorn.
- **Frontend concepts:** React + TypeScript scaffold (Vite), basic fetch calls, typed API client.
- **Database concepts:** PostgreSQL schema design, primary/foreign keys, SQLAlchemy Core/ORM basics, first Alembic migration.
- **Architecture concepts:** Why "fat route handlers" don't scale (felt, not just told).
- **Distributed systems concepts:** None yet — intentionally single-node, single-process, to set the baseline.
- **DevOps concepts:** Dockerfile, Docker Compose (api + postgres), `.env` management, Git basics, Git Flow branch naming.
- **Observability concepts:** Basic structured logging with `logging`/`structlog`.
- **Security concepts:** Input validation via Pydantic, basic CORS.
- **Testing concepts:** Unit Test vs Integration Test distinction; pytest + `httpx.AsyncClient` for endpoint tests; Fixture basics.
- **Practical tasks:** Build Product, Category CRUD endpoints; connect Postgres; write 10+ tests; Dockerize; push to GitHub with CI stub.
- **Deliverables:** Running containerized API, OpenAPI/Swagger docs, passing test suite, README with architecture diagram v0.
- **Definition of Done:** `docker compose up` boots API + DB; all CRUD endpoints pass integration tests; migrations are reproducible from scratch.
- **Common mistakes:** Business logic inside route handlers; no input validation; hardcoded secrets; missing indices on foreign keys.
- **Code review checklist:** Are handlers thin? Are Pydantic schemas separate from ORM models? Is the DB session properly scoped per-request?
- **Interview questions:** "Explain WSGI vs ASGI." "Why does FastAPI use Pydantic?" "What's the risk of putting SQL directly in a route handler?"
- **Stretch goals:** Add OpenAPI tags/examples; add a pre-commit hook (ruff/black/mypy).
- **Resources:** FastAPI official docs, "Architecture Patterns with Python" (Percival & Gregory) Ch. 1.

---

### Sprint 2 — Layered Architecture, Auth & Migrations Done Right

**Objective:** Refactor Sprint 1 into a proper layered architecture; add real authentication.

**Why this sprint exists:** Every subsequent sprint depends on a clean Service Layer / Repository boundary — retrofitting this later would mean touching every file.

- **Backend concepts:** Service Layer, Repository Pattern, Dependency Injection via FastAPI `Depends`, Decorator deep-dive, Context Manager (DB sessions), Dataclasses vs Pydantic models.
- **Frontend concepts:** Auth flow (login form, token storage, protected routes), Axios interceptor for `Authorization` header.
- **Database concepts:** Alembic migration workflow (autogenerate, review, apply), Composite Index on lookup columns.
- **Architecture concepts:** Layered Architecture (routers → services → repositories → models), separating domain schemas from persistence models.
- **Distributed systems concepts:** Stateless services (why JWT enables horizontal scaling vs server-side sessions).
- **DevOps concepts:** Multi-service Docker Compose, environment-based config (12-factor).
- **Observability concepts:** Request-ID middleware for log correlation.
- **Security concepts:** JWT (access/refresh), OAuth2 password flow, Bearer Token, Hashing + Salting (bcrypt/argon2), Basic Auth (for internal tools), API Key (for future partner integrations).
- **Testing concepts:** Mock vs Stub (mocking the repository in service-layer unit tests), Coverage baseline (target 80%+).
- **Practical tasks:** Implement User model, register/login/refresh endpoints, password hashing, protect Product write endpoints with role checks, migrate Sprint 1 code into layers.
- **Deliverables:** Auth working end-to-end from React; layered backend; coverage report.
- **Definition of Done:** No SQL/business logic in routers; all secrets via env vars; refresh token rotation works; tests cover service layer with mocked repositories.
- **Common mistakes:** Storing JWTs in localStorage without XSS mitigation; not rotating refresh tokens; leaking password hashes in logs.
- **Code review checklist:** Is auth logic isolated in its own service? Are repository interfaces (ABCs/Protocols) used so services don't depend on SQLAlchemy directly?
- **Interview questions:** "Why JWT over server sessions in a distributed system?" "Explain the Repository Pattern and why it aids testability." "What's the difference between authentication and authorization?"
- **Stretch goals:** Add OAuth2 social login; add rate limiting on `/login`.
- **Resources:** OWASP Authentication Cheat Sheet, "Architecture Patterns with Python" Ch. 2–4.

---

### Sprint 3 — Modular Monolith: Sellers, Attributes, Variants (DDD Entry Point)

**Objective:** Expand the domain (Sellers, Product Attributes, Product Variants, Warehouses) organized as bounded modules inside one deployable — the Modular Monolith.

**Why this sprint exists:** Real catalogs aren't flat product rows — variants (size/color), attributes, and multi-seller/multi-warehouse inventory introduce genuine domain complexity where DDD tactical patterns start paying off.

- **Backend concepts:** Domain-Driven Design basics (Entity, Value Object, Aggregate, Aggregate Root), Factory Pattern for constructing complex aggregates, MRO and multiple inheritance pitfalls, Duck Typing vs Protocols.
- **Frontend concepts:** Dynamic product forms driven by attribute schemas; typed discriminated unions in TS for variants.
- **Database concepts:** Modeling EAV-lite (Entity-Attribute-Value) vs JSONB columns trade-offs; QuerySet-equivalent query builders; N+1 Query problem introduced deliberately (list products with variants naively).
- **Architecture concepts:** Module boundaries inside a monolith (folders-as-bounded-contexts), Facade Pattern to expose module APIs internally.
- **Distributed systems concepts:** None new — but explicitly design module boundaries as *future service boundaries*.
- **DevOps concepts:** Seed/fixture data scripts for realistic catalog volume (100k+ products) for later performance work.
- **Observability concepts:** Log the N+1 query problem happening (query count per request) to make the pain visible.
- **Security concepts:** Authorization scoping (sellers can only edit their own products) — intro to row-level access control.
- **Testing concepts:** Fixture factories (factory_boy) for complex aggregates; Functional Test of "create variant with attributes."
- **Practical tasks:** Model Seller, Warehouse, Attribute, Variant; implement multi-warehouse stock per variant; deliberately trigger and log an N+1 query on the product list endpoint.
- **Deliverables:** Catalog supporting variants/attributes across sellers/warehouses; a documented, reproduced N+1 problem (screenshot of query log) to be fixed next sprint.
- **Definition of Done:** Aggregates enforce invariants (e.g., a variant can't reference a nonexistent attribute); module boundaries have no circular imports.
- **Common mistakes:** Anemic domain models (all logic in services, none in entities); leaking ORM models across module boundaries.
- **Code review checklist:** Does each module expose a clean internal API (not raw ORM models) to other modules?
- **Interview questions:** "What's an Aggregate Root and why does it matter for consistency boundaries?" "What causes an N+1 query and how do you detect it?"
- **Stretch goals:** Add a Strategy Pattern for pricing rules per seller.
- **Resources:** "Domain-Driven Design Distilled" (Vernon), "Cosmic Python" (Percival/Gregory) DDD chapters.

---

### Sprint 4 — Query Performance, select_related/prefetch_related, and Pagination

**Objective:** Fix the N+1 problem from Sprint 3, master query optimization, and implement real pagination for catalog browsing.

**Why this sprint exists:** Every backend job interview probes query performance. You need scars, not slides.

- **Backend concepts:** Lazy Loading vs Eager Loading, `select_related`/`prefetch_related` equivalents in SQLAlchemy (`joinedload`/`selectinload`), Generators/Iterators for streaming large result sets.
- **Frontend concepts:** Infinite scroll / "load more" UI wired to cursor pagination.
- **Database concepts:** Index, Composite Index, Covering Index, EXPLAIN/Execution Plan reading, Query Planner, Full Table Scan vs Sequential Scan vs Index Scan, Offset Pagination vs Cursor Pagination trade-offs.
- **Architecture concepts:** Read-model shaping (don't over-fetch; DTOs per endpoint).
- **Distributed systems concepts:** Why offset pagination breaks under concurrent writes (phantom pages) — early motivation for eventual consistency thinking.
- **DevOps concepts:** `pg_stat_statements` enabled locally for query analysis.
- **Observability concepts:** Query count + duration per request logged/asserted in tests (a query-count regression test).
- **Security concepts:** Guard against unbounded `limit` (DoS via huge page sizes).
- **Testing concepts:** Benchmark tests (pytest-benchmark) comparing before/after query counts and latency.
- **Practical tasks:** Add composite indices; rewrite the product list endpoint using eager loading; implement cursor-based pagination; run EXPLAIN ANALYZE on the top 3 slow queries and document findings.
- **Deliverables:** Product list endpoint at O(1) queries regardless of variant count; documented EXPLAIN output before/after; pagination in the API and UI.
- **Definition of Done:** No N+1 on any list endpoint (verified by test asserting query count); p95 latency for catalog list < 100ms locally at 100k rows.
- **Common mistakes:** Adding indices blindly without checking selectivity; offset pagination at scale; eager-loading everything (over-fetching).
- **Code review checklist:** Is there a test that fails if someone reintroduces an N+1 query?
- **Interview questions:** "Walk me through reading an EXPLAIN ANALYZE output." "Offset vs cursor pagination — when would you choose each?" "What's a covering index?"
- **Stretch goals:** Add `EXPLAIN` output to CI as a performance regression gate.
- **Resources:** "Use The Index, Luke", PostgreSQL official docs on query planning.

---

### Sprint 5 — Cart, Checkout & Transactional Integrity

**Objective:** Build Shopping Cart and Checkout with correct transaction boundaries, isolation levels, and concurrency control.

**Why this sprint exists:** Cart/checkout is where race conditions (two people buying the last item) become real and costly — the perfect vehicle for ACID and locking concepts.

- **Backend concepts:** Unit of Work pattern, Context Manager for transaction scope, Optimistic Concurrency via version columns.
- **Frontend concepts:** Optimistic UI updates for cart actions with rollback on failure.
- **Database concepts:** ACID, Transaction/Commit/Rollback/Savepoint, Isolation Levels (Read Committed, Repeatable Read, Serializable), Dirty Read/Non-repeatable Read/Phantom Read, MVCC, Optimistic Lock vs Pessimistic Lock, Row Lock vs Table Lock, Deadlock, Lost Update, Race Condition.
- **Architecture concepts:** Unit of Work as a transactional boundary abstraction spanning multiple repositories.
- **Distributed systems concepts:** Idempotency introduced (retrying "add to cart" safely).
- **DevOps concepts:** Load-testing script (Locust) simulating concurrent checkouts on the same product.
- **Observability concepts:** Log and alert on deadlock occurrences.
- **Security concepts:** CSRF considerations for state-changing cart endpoints.
- **Testing concepts:** Concurrency tests (two async clients racing on the last unit of stock); Integration Test with real Postgres (not sqlite) to catch isolation-level differences.
- **Practical tasks:** Implement Cart with per-user persistence; implement Checkout that decrements stock inside a transaction using row-level locks (`SELECT ... FOR UPDATE`); reproduce a Lost Update bug, then fix it with optimistic or pessimistic locking; write a Locust script simulating a flash-sale race.
- **Deliverables:** Checkout that never oversells stock under concurrent load (proven by the Locust test); a written incident report of the Lost Update bug you intentionally caused and fixed.
- **Definition of Done:** 100 concurrent checkout attempts on 10 units of stock result in exactly 10 successes, 90 correct "out of stock" responses, zero deadlocked stuck transactions.
- **Common mistakes:** Locking too broadly (table lock instead of row lock); holding transactions open across I/O calls (e.g., external API calls) causing lock contention.
- **Code review checklist:** Is the transaction as short-lived as possible? Is the isolation level explicitly chosen and justified?
- **Interview questions:** "Explain the difference between optimistic and pessimistic locking, and when you'd choose each." "What is MVCC and how does Postgres use it?" "How would you prevent overselling in a flash sale?"
- **Stretch goals:** Add a Redis-based distributed lock as an alternative strategy and benchmark it against `SELECT FOR UPDATE`.
- **Resources:** "Designing Data-Intensive Applications" (Kleppmann) Ch. 7, PostgreSQL Transaction Isolation docs.

---

### Sprint 6 — Orders, Payments (Mock), and the Outbox/Idempotency Pattern

**Objective:** Model the full Order lifecycle and integrate a mock Payment gateway with idempotency guarantees and reliable event publishing via the Outbox Pattern.

**Why this sprint exists:** Payments are the canonical example of "must never double-charge, must never lose an event" — this is where Idempotency and the Outbox Pattern stop being theory.

- **Backend concepts:** Idempotency keys, Outbox Pattern implementation (event table written in the same transaction as the order), Builder Pattern for constructing complex Order objects, Observer Pattern for order status change hooks.
- **Frontend concepts:** Order status timeline UI; handling "processing" states without blocking the UI.
- **Database concepts:** Payment Idempotency at the DB level (unique constraint on idempotency key), Order Workflow as a state machine table.
- **Architecture concepts:** Compensation Transaction concept introduced (refund as compensation for a failed post-payment step); Order Workflow / state machine design.
- **Distributed systems concepts:** Outbox Pattern, Inbox Pattern (dedup on the consumer side), Exactly Once vs At Least Once vs At Most Once delivery semantics (discussed, not yet fully implemented — Kafka comes in Sprint 9).
- **DevOps concepts:** A simple polling relay process (later replaced by Debezium/CDC conceptually) reading the outbox table.
- **Observability concepts:** Audit Log table for every order state transition.
- **Security concepts:** PCI-DSS awareness (never store raw card data — mock gateway only), TLS for payment endpoints.
- **Testing concepts:** Idempotency test (submit the same payment request twice, assert single charge); Contract Testing intro (mock payment gateway contract).
- **Practical tasks:** Implement Order state machine (pending → paid → fulfilled → completed / cancelled); build mock Payment Service with idempotency-key deduplication; implement the Outbox table + relay; add Audit Log writes on every transition.
- **Deliverables:** An order can be paid exactly once even if the client retries the payment request 10 times; every state transition is audit-logged.
- **Definition of Done:** Duplicate payment requests (same idempotency key) return the original result, never double-charge; outbox events are never lost even if the relay crashes mid-batch.
- **Common mistakes:** Publishing events directly from application code without the Outbox Pattern (dual-write problem — DB commit succeeds, event publish fails, or vice versa).
- **Code review checklist:** Is the outbox write in the *same* DB transaction as the business write? Is there a unique constraint enforcing idempotency, not just an application-level check (TOCTOU risk)?
- **Interview questions:** "What's the dual-write problem and how does the Outbox Pattern solve it?" "How do you design a payment API to be idempotent?" "Explain at-least-once vs exactly-once delivery."
- **Stretch goals:** Implement a Compensation Transaction end-to-end (payment succeeds, fulfillment fails → auto-refund).
- **Resources:** microservices.io (Outbox Pattern, Saga Pattern), Kleppmann Ch. 11 (Stream Processing).

---

### Sprint 7 — Caching, Redis & Performance Engineering

**Objective:** Introduce Redis across caching, sessions, and rate limiting; establish a performance benchmarking habit.

**Why this sprint exists:** By now the monolith is feature-rich but slow under load — the natural point to introduce caching, and to teach that caching is a correctness problem (invalidation) as much as a performance one.

- **Backend concepts:** Cache Aside pattern, Write Through vs Write Back, TTL design, Lua Script for atomic Redis operations, Bloom Filter for existence checks (e.g., "has this SKU ever existed").
- **Frontend concepts:** ETag/If-None-Match aware fetch client to leverage HTTP caching.
- **Database concepts:** Read Replica concept introduced (route heavy read traffic away from primary — simulated locally).
- **Architecture concepts:** Distributed Cache as a shared-state hazard between service instances; cache stampede prevention.
- **Distributed systems concepts:** Distributed Lock via Redis (Redlock discussion — including its criticisms), Cache invalidation strategies across multiple app instances.
- **DevOps concepts:** Redis added to Docker Compose with persistence (AOF) configured; benchmark harness (Locust/wrk) as a repeatable script in CI.
- **Observability concepts:** Cache hit/miss ratio metric exposed; latency histograms before/after caching.
- **Security concepts:** Session fixation risks with Redis-backed sessions; key-namespacing to avoid cross-tenant leakage.
- **Testing concepts:** Load Testing (Locust) with defined SLO targets (p95 < 200ms); Stress Testing to find the breaking point.
- **Practical tasks:** Cache product detail pages and category listings (cache-aside, TTL + explicit invalidation on write); implement HTTP Cache-Control/ETag on read endpoints; implement Redis-based rate limiting on auth endpoints; benchmark before/after with Locust and publish results in the README.
- **Deliverables:** Documented before/after latency and throughput numbers; a cache invalidation strategy doc explaining what can go stale and for how long.
- **Definition of Done:** Cache hit ratio > 80% on hot product pages in load test; stale-cache bugs covered by a regression test (update product → cache invalidated → next read is fresh).
- **Common mistakes:** Caching without an invalidation plan ("cache forever" bugs); caching per-user data in a shared cache key (data leak); thundering herd on cache expiry.
- **Code review checklist:** Is every cache write paired with an invalidation path? Are cache keys namespaced and TTL'd appropriately?
- **Interview questions:** "Explain cache-aside vs write-through and their trade-offs." "How do you prevent a cache stampede?" "How would you design a distributed rate limiter?"
- **Stretch goals:** Implement a Bloom Filter to short-circuit "product not found" DB lookups.
- **Resources:** "Designing Data-Intensive Applications" Ch. 3 & 11, Redis official docs on patterns.

---

### Sprint 8 — Async Python, Background Jobs & the GIL

**Objective:** Deeply understand Python concurrency (GIL, threads, processes, asyncio) and offload slow work (emails, image processing, report generation) to Celery/RabbitMQ.

**Why this sprint exists:** "Explain the GIL" is asked in nearly every middle+ Python interview, and background job design (Celery + broker) is a daily production concern.

- **Backend concepts:** GIL explained precisely (what it protects, why it exists, when it doesn't matter), Thread vs Process vs Coroutine, AsyncIO Event Loop internals, `async`/`await` mechanics, Future vs Task, ThreadPoolExecutor vs ProcessPoolExecutor, CPU-bound vs I/O-bound workload identification.
- **Frontend concepts:** Polling or WebSocket for background job status ("your report is generating...").
- **Database concepts:** Connection Pool sizing for async workloads (avoiding pool exhaustion under concurrency).
- **Architecture concepts:** Where async buys you nothing (CPU-bound work) vs where it shines (I/O-bound fan-out, e.g., calling 5 external APIs concurrently).
- **Distributed systems concepts:** Producer/Consumer model, Queue semantics, Retry with Exponential Backoff for failed jobs.
- **DevOps concepts:** RabbitMQ added to Docker Compose; Celery worker + beat scheduler containers; Flower for job monitoring.
- **Observability concepts:** Job success/failure metrics; dead-letter visibility for permanently failed jobs.
- **Security concepts:** Never trust job payloads blindly (validate before executing); avoid pickle for untrusted task serialization (use JSON).
- **Testing concepts:** Testing async code correctly (pytest-asyncio), testing Celery tasks in eager mode plus one real integration test against a real broker.
- **Practical tasks:** Move order-confirmation emails and invoice PDF generation to Celery tasks; implement retry with exponential backoff and a dead-letter queue for failed jobs; write a CPU-bound benchmark (image resize) comparing threads vs processes vs plain asyncio to prove the GIL's effect empirically.
- **Deliverables:** A benchmark report showing measured GIL impact (asyncio/threads for I/O-bound vs multiprocessing for CPU-bound); background email/PDF pipeline with retries and a DLQ.
- **Definition of Done:** Slow operations no longer block the request/response cycle; failed jobs retry with backoff and land in a DLQ after N attempts, visible in Flower.
- **Common mistakes:** Using `threading` for CPU-bound work expecting a speedup (GIL blocks it); blocking calls inside async route handlers (killing the event loop); unbounded task retries without backoff.
- **Code review checklist:** Is every external I/O call in an async handler actually non-blocking (`httpx.AsyncClient`, async DB driver)? Do background tasks have idempotent handlers (safe to retry)?
- **Interview questions:** "Explain the GIL and its practical implications." "When would you choose multiprocessing over asyncio?" "How do you design a retry strategy for background jobs?"
- **Stretch goals:** Add Celery Canvas (chains/chords) for a multi-step report pipeline.
- **Resources:** "Python Concurrency with asyncio" (Fowler), Celery official docs, David Beazley's GIL talks.

---

### Sprint 9 — Event-Driven Architecture: Kafka, Sagas & CQRS Foundations

**Objective:** Introduce Kafka as the cross-domain event backbone; implement the Saga Pattern for the order/inventory/payment workflow; introduce CQRS for the product catalog read model.

**Why this sprint exists:** This is the architectural pivot point — the system stops being a single transactional monolith and starts behaving like a distributed system with eventual consistency, which is the hardest and most interview-relevant topic in the whole roadmap.

- **Backend concepts:** Event Bus abstraction, Saga Pattern (choreography vs orchestration — implement orchestration), CQRS (separate write model in Postgres from a read model projection), Event Sourcing discussed conceptually and applied narrowly to Order history.
- **Frontend concepts:** Server-Sent Events (SSE) for live order-status updates driven by consumed events.
- **Database concepts:** Eventual Consistency accepted explicitly for cross-service state; Snapshot Isolation revisited in the context of the read-model projector.
- **Architecture concepts:** CAP Theorem and PACELC applied to this exact system ("during a network partition between Order and Inventory, do we favor consistency or availability?"); Split Brain scenario discussion.
- **Distributed systems concepts:** Kafka core concepts — Producer, Consumer, Consumer Group, Topic, Partition, Offset; Exactly Once/At Least Once/At Most Once revisited with Kafka's actual guarantees; Dead Letter Queue for poison messages.
- **DevOps concepts:** Kafka + Zookeeper/KRaft in Docker Compose; topic creation/partitioning strategy documented.
- **Observability concepts:** Consumer lag monitoring; event-flow tracing across services (precursor to Sprint 14's full tracing).
- **Security concepts:** Topic-level ACLs discussion; message schema validation to prevent poison-pill events.
- **Testing concepts:** Testing event-driven flows (publish event → assert consumer side-effect) using an embedded/test Kafka broker; Contract Testing for event schemas.
- **Practical tasks:** Publish `OrderCreated`, `InventoryReserved`, `PaymentSucceeded/Failed` events to Kafka via the outbox relay; implement a Saga Orchestrator service that reacts to these events and issues compensations on failure; build a read-model projector maintaining a denormalized "Order Summary" table for fast dashboard queries (CQRS).
- **Deliverables:** A working saga that correctly compensates (releases reserved stock, refunds) when payment fails after inventory is reserved; a CQRS read model kept in sync via consumed events.
- **Definition of Done:** Killing the Payment service mid-flow and restarting it results in the saga resuming correctly (no stuck orders); consumer lag is visible on a dashboard.
- **Common mistakes:** Choreography sprawl (too many services reacting to each other's events with no central visibility) — chosen orchestration for this reason and you should be able to defend it; forgetting idempotent consumers (reprocessing the same Kafka message on rebalance).
- **Code review checklist:** Is every Kafka consumer idempotent (safe to process the same message twice)? Does the saga have an explicit compensation path for every failure branch?
- **Interview questions:** "Explain CAP theorem with a concrete example from your project." "Choreography vs orchestration sagas — trade-offs?" "How does Kafka achieve at-least-once delivery, and how do you get effectively-once at the application level?"
- **Stretch goals:** Implement a basic Event Sourcing store for the Order aggregate (rebuild state by replaying events).
- **Resources:** Kleppmann Ch. 9 & 11, microservices.io Saga Pattern, Confluent Kafka documentation.

---

### Sprint 10 — Search, Recommendations & Polyglot Persistence

**Objective:** Add Elasticsearch/OpenSearch-powered product search and a basic collaborative-filtering recommendation system; introduce MongoDB where it clearly beats Postgres for this data shape.

**Why this sprint exists:** Search relevance and recommendations are common "distinguishing" portfolio features, and this sprint teaches *when* to reach for a non-relational store instead of defaulting to Postgres for everything.

- **Backend concepts:** Indexing pipelines (sync Postgres → Elasticsearch on write, via the outbox events from Sprint 6/9), Adapter Pattern to isolate the search client behind an interface.
- **Frontend concepts:** Search-as-you-type UI with debouncing; facet/filter sidebar wired to ES aggregations.
- **Database concepts:** When MongoDB beats Postgres (flexible review documents with nested replies, rapidly evolving attribute schemas) vs when it doesn't (anything needing strong transactional guarantees) — a written trade-off decision.
- **Architecture concepts:** Polyglot persistence — the Catalog service now reads from Postgres (source of truth), Elasticsearch (search), and MongoDB (reviews) simultaneously; keeping these in sync via events.
- **Distributed systems concepts:** Eventual consistency between the source of truth and the search index (and how to detect drift).
- **DevOps concepts:** Elasticsearch/OpenSearch and MongoDB added to Docker Compose; index mapping versioning strategy.
- **Observability concepts:** Search latency and zero-result-rate metrics; reindex job monitoring.
- **Security concepts:** Sanitizing search input to prevent query injection into ES query DSL.
- **Testing concepts:** Integration tests against a real (test-container) Elasticsearch instance; relevance regression tests (does searching "red shoes" return red shoes first?).
- **Practical tasks:** Build the ES index and sync pipeline; implement search endpoint with filters/facets/pagination; move Reviews to MongoDB with a simple recommendation job (item-based collaborative filtering, computed as a nightly Celery task) writing "customers also bought" data back to Postgres/Redis for fast reads.
- **Deliverables:** Full-text search with facets; a "customers also bought" widget backed by a real (if simple) recommendation computation.
- **Definition of Done:** Search index never silently drifts from Postgres for more than the documented sync SLA; recommendation job runs on schedule and results are cached.
- **Common mistakes:** Treating Elasticsearch as a primary datastore (it isn't durable/transactional in the way you need); N+1-style over-querying MongoDB the same way you did Postgres in Sprint 3.
- **Code review checklist:** Is there a clear "source of truth" documented for every piece of data now living in 3 stores? Is the search client behind an interface so ES could be swapped for OpenSearch without touching business logic?
- **Interview questions:** "How would you keep a search index in sync with your primary database?" "When would you choose MongoDB over PostgreSQL?" "How do you handle relevance tuning in Elasticsearch?"
- **Stretch goals:** Add a simple embeddings-based ("semantic") search layer alongside keyword search.
- **Resources:** Elasticsearch: The Definitive Guide, MongoDB schema design patterns docs.

---

### Sprint 11 — Splitting the Monolith: Microservices, API Gateway & gRPC

**Objective:** Extract 2–3 bounded contexts (e.g., Catalog, Order, Payment) into independently deployable services communicating over gRPC internally and REST externally, behind an API Gateway. The Auth Service and Payment Service remain FastAPI; the extracted domain services are implemented in Django/DRF where their CRUD-heavy and admin-oriented workflows benefit from Django's batteries-included stack.

**Why this sprint exists:** This is where "modular monolith" pays off — module boundaries designed since Sprint 3 become service boundaries, proving the value of that early discipline.

- **Backend concepts:** gRPC + Protocol Buffers for internal service-to-service calls, GraphQL evaluated as an alternative API-gateway pattern (implemented for one read-heavy aggregation use case, e.g., "order detail with product + seller info"), Facade/Adapter patterns at service boundaries.
- **Frontend concepts:** Single API Gateway endpoint for the client (no direct multi-service calls from React).
- **Database concepts:** Database-per-service enforced (no cross-service joins); data duplication trade-offs discussed explicitly.
- **Architecture concepts:** Microservice vs Monolith trade-offs revisited with real experience now; Service Mesh concept introduced (not yet implemented — arrives with Kubernetes in Sprint 13); Sidecar pattern explained.
- **Distributed systems concepts:** Service Discovery (DNS-based for now), Health Check endpoints per service, Fault Tolerance basics (what happens when the Catalog service is down but Order isn't).
- **DevOps concepts:** Each service gets its own Dockerfile and CI pipeline stage; Docker Compose grows to reflect the multi-service topology.
- **Observability concepts:** Per-service logs now need correlation — Request-ID propagation across service boundaries via gRPC metadata (full tracing arrives in Sprint 14).
- **Security concepts:** Internal-only network for gRPC (not exposed publicly); mTLS discussed as the production answer (deferred to Kubernetes/service-mesh sprint).
- **Testing concepts:** Contract Testing formalized (Pact-style) between the Gateway and each downstream service, since integration tests across real network boundaries are now expensive.
- **Practical tasks:** Extract Catalog into a standalone Django/DRF service with its own DB and Dockerfile; keep the Auth Service and Payment Service as FastAPI services; implement an API Gateway (FastAPI-based) that fans out to them via gRPC and assembles responses; add health-check endpoints to every service; write contract tests for each service boundary.
- **Deliverables:** A genuinely multi-service system, each independently deployable and independently testable; documented service boundary diagram with justifications.
- **Definition of Done:** Each service can be deployed independently without redeploying the others; the Gateway degrades gracefully (partial data + error) if one downstream service is unavailable.
- **Common mistakes:** Splitting services along technical layers instead of business capabilities (a classic "distributed monolith" anti-pattern); sharing a database across services "just for now."
- **Code review checklist:** Does any service reach directly into another service's database? Is there a documented API contract (proto file / OpenAPI) per service?
- **Interview questions:** "How do you decide service boundaries?" "REST vs gRPC vs GraphQL — when would you use each?" "What is a 'distributed monolith' and how do you avoid building one?"
- **Stretch goals:** Add a simple Service Mesh proof-of-concept locally (Linkerd/Istio) ahead of Sprint 13.
- **Resources:** "Building Microservices" (Newman), gRPC official docs, "Microservices Patterns" (Richardson).

---

### Sprint 12 — CI/CD, Multi-Stage Docker & Infrastructure as Code

**Objective:** Build a real CI/CD pipeline (lint → test → build → scan → push → deploy) with multi-stage Docker builds and introduce Terraform/Ansible for infrastructure provisioning.

**Why this sprint exists:** Deploying by hand doesn't scale past sprint 1; production teams live and die by their pipelines — this sprint makes shipping a non-event.

- **Backend concepts:** None new — this sprint is a deliberate DevOps-heavy pause to consolidate.
- **Frontend concepts:** Frontend build pipeline (type-check, lint, build, deploy static assets to S3/MinIO + CDN pattern).
- **Database concepts:** Migration automation as a CI/CD gate (migrations run and are verified before deploy).
- **Architecture concepts:** Immutable infrastructure principle; environment parity (dev/staging/prod).
- **Distributed systems concepts:** Rolling Update strategy explained (still pre-Kubernetes, using Docker Compose/Swarm-style thinking as a bridge).
- **DevOps concepts:** GitHub Actions workflows (matrix builds, caching layers), Multi-stage Docker Build (build stage vs slim runtime stage), image vulnerability scanning, Semantic Versioning for releases, Terraform for provisioning a cloud DB/registry, Ansible for config management of a VM, Git workflows deep-dive (Rebase vs Merge, Cherry-pick, Squash, Fast Forward, Detached HEAD, Trunk Based Development vs Git Flow compared with trade-offs).
- **Observability concepts:** Build/deploy metrics (lead time, deploy frequency — DORA metrics awareness).
- **Security concepts:** Secrets management in CI (GitHub Secrets, never in the repo); dependency vulnerability scanning (`pip-audit`/`npm audit`) as a CI gate.
- **Testing concepts:** CI runs the full pyramid (unit → integration → contract) with fail-fast ordering; Coverage gate enforced in CI.
- **Practical tasks:** Write GitHub Actions workflows for every service (test + build + push to a container registry); convert all Dockerfiles to multi-stage builds and measure image size before/after; write a minimal Terraform config provisioning a managed Postgres + container registry; automate migrations as a pre-deploy CI step.
- **Deliverables:** Green-to-green pipeline: a merged PR results in a deployed system with zero manual steps; documented image size reduction from multi-stage builds.
- **Definition of Done:** CI fails the build on lint/type/test/coverage/vulnerability failures; a rollback procedure is documented and tested at least once.
- **Common mistakes:** No caching in CI (slow feedback loops); baking secrets into images; skipping the vulnerability scan step under time pressure.
- **Code review checklist:** Does the pipeline fail fast on the cheapest checks first (lint before integration tests)? Is the Docker image minimal (no build tools in the runtime layer)?
- **Interview questions:** "Walk me through a CI/CD pipeline you've built." "Why use multi-stage Docker builds?" "Rebase vs merge — when do you use each, and why does it matter for a shared branch?"
- **Stretch goals:** Add ArgoCD-style GitOps deployment (deferred fully to Sprint 13 with Kubernetes).
- **Resources:** "The DevOps Handbook", GitHub Actions docs, Terraform "Up & Running".

---

### Sprint 13 — Kubernetes-Ready: Pods, Deployments, Helm & Autoscaling

**Objective:** Move the entire multi-service system onto Kubernetes with Helm charts, ConfigMaps/Secrets, health probes, and autoscaling.

**Why this sprint exists:** Kubernetes is introduced only now — deliberately — because it's genuinely hard to appreciate Pods/Services/Ingress until you already have a real multi-service system with real deployment pain to solve.

- **Backend concepts:** Graceful Shutdown handling in FastAPI (SIGTERM handling, draining in-flight requests) — required for Kubernetes rolling updates to be safe.
- **Frontend concepts:** Served via Ingress + static hosting; environment-specific config injected at build/deploy time.
- **Database concepts:** StatefulSet for Postgres (in a local/dev cluster context) vs using a managed DB in real prod (documented trade-off, since running your own stateful DB in k8s is itself a debated practice).
- **Architecture concepts:** The Kubernetes object model as an architecture in itself (declarative desired-state reconciliation).
- **Distributed systems concepts:** Liveness Probe vs Readiness Probe (and why conflating them causes cascading outages), Horizontal Pod Autoscaler, Rolling Update, Blue-Green Deployment, Canary Deployment strategies compared.
- **DevOps concepts:** Pod, ReplicaSet, Deployment, Service, Ingress, Namespace, ConfigMap, Secret, DaemonSet, Job, CronJob (for the nightly recommendation job from Sprint 10), Helm charts (templating values per environment).
- **Observability concepts:** `kubectl logs`/`describe`/`top` as first-response debugging tools; resource requests/limits tuned from observed usage.
- **Security concepts:** Kubernetes Secrets (and their limitations — not encrypted at rest by default, sealed-secrets discussion); NetworkPolicy basics restricting pod-to-pod traffic.
- **Testing concepts:** Smoke tests run post-deploy inside the cluster; Helm chart linting in CI.
- **Practical tasks:** Write Kubernetes manifests/Helm charts for every service; configure liveness/readiness probes correctly (readiness checks DB connectivity, liveness doesn't); set up HPA based on CPU/memory; convert the recommendation job to a CronJob; deploy to a local cluster (kind/minikube) via CI.
- **Deliverables:** `helm install atlascommerce` brings up the entire system on a local cluster; documented HPA behavior under the Sprint 5/7 load-testing scripts re-run against the cluster.
- **Definition of Done:** A pod killed mid-request drains gracefully with zero dropped requests (verified under load); HPA scales pod count up under the Locust test and back down after.
- **Common mistakes:** Readiness and liveness probes checking the same thing (a slow DB connection shouldn't kill a healthy process, only mark it not-ready); missing resource requests/limits causing noisy-neighbor problems; storing secrets in ConfigMaps instead of Secrets.
- **Code review checklist:** Does every Deployment define resource requests/limits and both probe types correctly? Are Secrets never committed to the Helm chart repo in plaintext?
- **Interview questions:** "Explain the difference between liveness and readiness probes." "How does a Horizontal Pod Autoscaler decide to scale?" "Blue-green vs canary deployment — trade-offs?"
- **Stretch goals:** Add ArgoCD for GitOps-based continuous deployment into the cluster.
- **Resources:** "Kubernetes Up & Running" (Hightower et al.), Helm official docs.

---

### Sprint 14 — Full Observability: Metrics, Logs, Traces & SLOs

**Objective:** Instrument the entire system with Prometheus, Grafana, Loki, OpenTelemetry, Jaeger, and Sentry; define and monitor real SLIs/SLOs/SLAs.

**Why this sprint exists:** You cannot operate a distributed system you can't see. This sprint turns every previous sprint's "it works on my machine" into "here's the dashboard proving it works in production."

- **Backend concepts:** OpenTelemetry instrumentation (auto + manual spans) across every service; structured logging correlated with trace IDs.
- **Frontend concepts:** Sentry frontend error tracking + basic real-user-monitoring (page load timings).
- **Database concepts:** Query-level tracing (spans around DB calls) to catch regressions like Sprint 4's N+1 problem automatically going forward.
- **Architecture concepts:** The three pillars of observability (Metrics, Logs, Tracing) and how they complement each other; APM concept tying them together.
- **Distributed systems concepts:** Distributed tracing across the gRPC/Kafka boundaries from Sprints 9 & 11 — following one request across 4 services and a Kafka hop in a single Jaeger trace.
- **DevOps concepts:** Prometheus scrape configs, Grafana dashboards as code (JSON provisioning), Loki for log aggregation, Alertmanager rules.
- **Observability concepts:** SLI (e.g., "checkout success rate"), SLO (e.g., "99.5% over 30 days"), SLA (customer-facing commitment) explicitly defined for 3 critical user journeys (browse, checkout, search); Alerting rules tied to SLO burn rate, not just raw thresholds.
- **Security concepts:** Ensure logs never contain PII/secrets (log scrubbing); Sentry data-scrubbing configuration.
- **Testing concepts:** Synthetic monitoring / smoke tests that exercise the critical path continuously and feed the SLO dashboard.
- **Practical tasks:** Instrument every service with OpenTelemetry and export to Jaeger; expose Prometheus metrics (request rate, error rate, duration — the RED method) from every service; build Grafana dashboards for each critical journey; wire Sentry into both backend and frontend; write Alertmanager rules for SLO burn-rate alerts.
- **Deliverables:** A single Jaeger trace showing a checkout request crossing Gateway → Order → Kafka → Inventory → Payment; Grafana dashboards for RED metrics per service and SLO status per journey; documented SLI/SLO/SLA definitions.
- **Definition of Done:** Every service exposes `/metrics` and structured logs with trace-ID correlation; an intentionally-introduced regression (re-add the Sprint 4 N+1 bug) is visible on the dashboard within minutes without reading code.
- **Common mistakes:** Instrumenting everything with no signal (alert fatigue from too many low-value alerts); logging at DEBUG level in production (cost and noise); traces without sampling strategy at scale.
- **Code review checklist:** Does every new endpoint emit a span and RED metrics automatically via shared middleware, or does each developer have to remember to add it? Are alerts tied to symptoms (SLO burn) rather than causes (CPU%) where possible?
- **Interview questions:** "Explain the RED and USE methods for monitoring." "What's the difference between an SLI, SLO, and SLA?" "How would you debug a slow request across 5 microservices in production?"
- **Stretch goals:** Add exemplars linking Prometheus metrics directly to Jaeger traces.
- **Resources:** "Distributed Tracing in Practice" (O'Reilly), Google SRE Book (Ch. 4 — SLOs), OpenTelemetry docs.

---

### Sprint 15 — Resilience, Chaos, Load Testing & Interview Readiness

**Objective:** Harden the system against real failure modes (Circuit Breaker, Bulkhead, Backpressure, Rate Limiting/Throttling, HA/DR), run chaos and load tests against it, and consolidate everything into interview-ready explanations.

**Why this sprint exists:** The final sprint proves the system survives failure, not just success — and converts 15 sprints of scars into confident, structured interview answers.

- **Backend concepts:** Circuit Breaker (implemented around the gRPC calls to Payment/Inventory), Bulkhead Pattern (isolating thread/connection pools per downstream dependency so one slow dependency can't starve the whole service), Graceful Degradation (catalog still browsable if recommendations service is down).
- **Frontend concepts:** UI graceful-degradation states (skeleton/fallback content when a non-critical service is down).
- **Database concepts:** Read Replica failover drill, Leader-Follower vs Master-Master replication trade-offs, Failover/Disaster Recovery drill (kill primary, promote replica, measure RTO/RPO), Hot Standby vs Cold Standby discussed.
- **Architecture concepts:** High Availability (HA) design review of the whole system end-to-end; a formal Architecture Decision Record (ADR) written for every major trade-off made across all 15 sprints.
- **Distributed systems concepts:** Retry Policy with jitter, Backpressure handling (what happens when Kafka consumers can't keep up), Timeout tuning (Connection Timeout vs Read Timeout vs Write Timeout) at every network hop, Feature Flag for safely toggling risky features in production.
- **DevOps concepts:** Chaos engineering drill (kill random pods/services under load with a script, akin to a mini Chaos Monkey) run against the Kubernetes cluster from Sprint 13.
- **Observability concepts:** Post-incident review process — run the chaos drill, then write a real incident postmortem using the dashboards from Sprint 14.
- **Security concepts:** Final OWASP Top 10 pass across the whole system (SQL Injection, XSS, CSRF, CORS, SSRF, XXE, Clickjacking) with a documented mitigation for each; final dependency and container image security scan.
- **Testing concepts:** Full test pyramid audit (Unit/Integration/Functional/End-to-End coverage report), final Load Testing + Stress Testing campaign against the whole cluster with results compared against the SLOs defined in Sprint 14.
- **Practical tasks:** Implement Circuit Breaker + Bulkhead around the riskiest downstream calls; run a chaos drill (kill the Payment pod during an active load test) and observe/tune the saga's compensation behavior; run a DB failover drill and measure recovery time; write ADRs for the 10 biggest architectural decisions made across the roadmap; do 2 full mock system-design interviews using AtlasCommerce as the running example.
- **Deliverables:** A chaos-drill report with graphs (before/during/after the induced failure); a stack of ADRs; a portfolio-ready README with architecture diagrams, trade-off explanations, and a "lessons learned" section; a rehearsed 10-minute system-design walkthrough of AtlasCommerce.
- **Definition of Done:** The system survives a killed dependency mid-load-test with graceful degradation (not a cascading outage) and self-heals per Kubernetes's reconciliation loop; every OWASP Top 10 item has a documented, implemented mitigation; you can whiteboard the full architecture from memory in under 10 minutes.
- **Common mistakes:** Circuit breakers with no fallback (they just turn one error into another); chaos testing skipped because "it's scary" — which is precisely why it matters; treating security as a final checklist instead of something reinforced throughout (which is why it's been present since Sprint 2).
- **Code review checklist:** Does every external call have a timeout, a retry policy, and a circuit breaker where appropriate? Is there a documented fallback behavior for every non-critical dependency?
- **Interview questions:** "Design an e-commerce checkout system" (use AtlasCommerce as your answer). "How do you prevent one failing dependency from taking down your whole system?" "Walk me through how you'd design for high availability and disaster recovery." "What was the hardest bug you fixed in this project and how did you diagnose it?"
- **Stretch goals:** Publish the postmortem and ADRs as a public blog series — this becomes your interview talking points and your portfolio content simultaneously.
- **Resources:** "Release It!" (Nygard) — Circuit Breaker/Bulkhead origin text, Google SRE Book (Ch. 8 — Postmortems, Ch. 26 — Data Integrity), OWASP Top 10 official docs.

---

## 4. Technology Timeline

| Sprint | New technologies introduced | Reason |
|---|---|---|
| 1 | FastAPI, PostgreSQL, SQLAlchemy, Docker, Docker Compose, Git | Baseline working system |
| 2 | Alembic, JWT/OAuth2 | Real persistence + auth |
| 3 | (DDD patterns, no new infra) | Domain complexity before more infra |
| 4 | pg_stat_statements, EXPLAIN tooling | Query performance discipline |
| 5 | Locust | Concurrency/load proof |
| 6 | (Outbox pattern, no new infra) | Reliability pattern before messaging infra |
| 7 | Redis | Caching, sessions, rate limiting |
| 8 | RabbitMQ, Celery, Flower | Background jobs |
| 9 | Kafka | Cross-service events, sagas, CQRS |
| 10 | Elasticsearch/OpenSearch, MongoDB, MinIO/S3 | Search, polyglot persistence, assets |
| 11 | gRPC, GraphQL (limited), API Gateway | Service decomposition |
| 12 | GitHub Actions, Terraform, Ansible | CI/CD & IaC |
| 13 | Kubernetes, Helm | Orchestration |
| 14 | Prometheus, Grafana, Loki, OpenTelemetry, Jaeger, Sentry | Full observability |
| 15 | Chaos scripts, Django/DRF mini-project (admin tools, run as a parallel side-track from Sprint 6 onward) | Resilience + comparative framework exposure |

*Django/DRF and Flask are deliberately run as a **parallel side-track**, not a main-line sprint: build the Internal/Admin Tools module in Django+DRF starting around Sprint 6 (once the domain is rich enough to admin), and one small Flask microservice (e.g., a simple webhook receiver) around Sprint 11 — so you can compare all three frameworks on the same real domain instead of learning them in the abstract.*

---

## 5. Concept Coverage Matrix

Legend: **I** = Introduced · **P** = Practiced/Reinforced · **M** = Mastered (used under load/failure and defended in an interview-style writeup)

| Concept group | Introduced | Practiced | Mastered |
|---|---|---|---|
| REST/HTTP fundamentals (REST, CRUD, Endpoint, Resource, Stateless, Safe/Idempotent Method, HTTP Methods/Status Codes, Headers, ETag, Cache-Control) | S1 | S2, S7 | S14 |
| Auth (JWT, OAuth2, Bearer/Basic/API Key, Hashing/Salting) | S2 | S6, S11 | S15 (OWASP pass) |
| API paradigms (OpenAPI/Swagger, GraphQL, gRPC, WebSocket, SSE, Long Polling) | S1, S11 | S9, S11 | S15 |
| Python concurrency (GIL, Thread, Process, Coroutine, AsyncIO, Event Loop, async/await, Future, Task, Pools) | S8 | S9, S10 | S15 |
| Python language internals (Generator, Iterator, Decorator, Context Manager, Descriptor, Metaclass, Monkey Patching, Duck Typing, MRO, Dataclass, Slots, Weak Reference, Pickle) | S1–S3 | S4, S8 | S15 |
| ORM & Query Performance (ORM, Lazy/Eager Loading, select_related/prefetch_related, QuerySet, Migration, N+1, Index types, EXPLAIN) | S1 | S3, S4 | S14 |
| Transactions & Concurrency Control (ACID, Isolation Levels, MVCC, Locks, Deadlock, Race Condition, Idempotency) | S5 | S6, S9 | S15 |
| Distributed data (CAP/PACELC, Consistency models, Distributed Lock, Consensus, Leader Election, Split Brain, Replication, Sharding, Partitioning) | S9 | S13, S15 | S15 |
| Resilience patterns (Retry/Backoff, Circuit Breaker, Bulkhead, Rate Limiting, Throttling, Backpressure) | S7 (rate limiting) | S8 (retry) | S15 (circuit breaker, bulkhead, backpressure) |
| Messaging patterns (Saga, CQRS, Event Sourcing, Outbox/Inbox, Producer/Consumer, Queue/Topic/Exchange, DLQ) | S6 | S9 | S15 |
| Design patterns (DI, Repository, Service Layer, UoW, Factory, Builder, Adapter, Facade, Strategy, Observer, Singleton) | S2, S3 | S6, S10 | S15 |
| Architecture principles (SOLID, DRY, KISS, YAGNI, Clean/Hexagonal/Onion Architecture, DDD, Layered Architecture) | S2, S3 | throughout | S15 (ADRs) |
| Service architecture (Microservice/Monolith, API Gateway, Reverse Proxy, LB, Service Discovery, Service Mesh, Sidecar, Health Check) | S11 | S13 | S15 |
| Messaging infra (RabbitMQ, Kafka, Redis Streams) | S8, S9 | S9 | S15 |
| Caching (Redis, Cache Aside, Write Through/Back, TTL, Pub/Sub, Distributed Cache, Lua Script, Bloom Filter) | S7 | S9, S10 | S15 |
| Containers (Docker, Dockerfile, Image, Container, Volume, Network, Layer, Multi-stage Build, Compose, Healthcheck) | S1 | S11, S12 | S13 |
| Kubernetes (Pod, ReplicaSet, Deployment, Service, Ingress, Namespace, ConfigMap, Secret, StatefulSet, DaemonSet, Job, CronJob, HPA, Rolling/Blue-Green/Canary) | S13 | S13 | S15 |
| Observability (Prometheus, Grafana, OTel, Jaeger, Loki, Metrics/Logs/Tracing, APM, SLI/SLO/SLA, Alerting) | S14 | S14 | S15 |
| CI/CD & IaC (GitHub Actions, GitLab CI, Jenkins, ArgoCD, Helm, Terraform, Ansible) | S12 | S13 | S15 |
| Git workflows (Merge, Rebase, Cherry-pick, Squash, Fast Forward, Detached HEAD, Git Flow, Trunk Based Dev, SemVer) | S1 | S12 | S15 |
| Testing (Unit/Integration/Functional/E2E, Mock/Stub/Fixture, Coverage, Contract, Load/Stress Testing, Benchmark, Profiling) | S1 | S4, S5, S9, S11 | S14, S15 |
| Performance (Latency, Throughput, Concurrency vs Parallelism, CPU/IO Bound, Memory Leak, Bottleneck) | S4 | S7, S8 | S15 |
| Security (SQL Injection, XSS, CSRF, CORS, SSRF, XXE, Clickjacking, OWASP Top 10, Encryption, TLS, HMAC) | S2 | throughout | S15 (dedicated pass) |
| Domain-specific patterns (Inventory Reservation/Sync, Stock Consistency, Payment Idempotency, Order Workflow, Compensation Transaction, Audit Log, Soft Delete, Feature Flag) | S5, S6 | S9 | S15 |
| High availability (Sticky Session, Graceful Shutdown/Degradation, Liveness/Readiness Probe, Timeouts, Keep Alive, Failover, HA, DR, Hot/Cold Standby, Read Replica, Leader-Follower/Master-Master) | S13 | S13 | S15 (failover drill) |

---

## 6. Portfolio Outcome

AtlasCommerce stands out because it is **one coherent system with visible history**, not fifteen disconnected demos:

- A hiring manager can trace a single feature (checkout) from a naive Sprint-1 implementation through locking bugs (Sprint 5), idempotent payments (Sprint 6), sagas (Sprint 9), microservice extraction (Sprint 11), and a chaos drill proving it survives failure (Sprint 15) — this is a **narrative**, not a feature list.
- It demonstrates the exact things Middle+/Senior interviews probe: query optimization with real EXPLAIN output, a documented race-condition bug you caused and fixed, a saga that correctly compensates, dashboards proving SLOs are met, and ADRs justifying every trade-off.
- The repo's commit history itself becomes evidence of engineering maturity — refactors, incident writeups, and a chaos-drill postmortem are things most portfolio projects simply don't have.
- It's technology-diverse *for a reason* (Django/DRF and Flask as deliberate comparisons, not resume-padding), which reads as informed judgment rather than tutorial-hopping.

---

## 7. Interview Readiness Summary

After Sprint 15 you should be able to confidently discuss, with concrete examples from AtlasCommerce:

- **Backend/Python:** GIL and concurrency model choices, async vs sync trade-offs, decorators/context managers/descriptors, ORM pitfalls (N+1, lazy loading), idempotency design.
- **Database:** Transaction isolation levels and their real failure modes, indexing and query-plan reading, replication/failover, when to reach for a non-relational store.
- **Distributed systems:** CAP/PACELC in a real scenario, sagas vs 2PC, exactly-once vs at-least-once delivery, consistency trade-offs you actually made and can defend.
- **DevOps:** A full CI/CD pipeline you built, multi-stage Docker rationale, Kubernetes probes/autoscaling/rollout strategies you configured and tested.
- **Architecture:** SOLID/DDD/Clean Architecture applied (not just defined), microservice boundary decisions with trade-offs, resilience patterns (circuit breaker/bulkhead) you implemented and chaos-tested.
- **Testing:** The full test pyramid applied to a real system, including load/stress/chaos testing and what each caught.
- **Observability:** Reading a distributed trace to debug a cross-service latency issue, defining and monitoring real SLIs/SLOs.

You will not be reciting definitions — you'll be describing decisions you made, bugs you caused on purpose, and incidents you recovered from, which is precisely what separates a Middle+/Senior candidate from someone who has only followed tutorials.
