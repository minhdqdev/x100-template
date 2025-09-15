# Django Best Practices (2025 Edition)

## 1. Project layout & config

- Use a two-tier layout: `repo/` → `src/` package + `deploy/` (docker, compose, k8s, terraform, scripts).
- Split settings by environment with a single entrypoint:
    - `src/config/settings/base.py`, `local.py`, `test.py`, `prod.py`.

    - Select via `DJANGO_SETTINGS_MODULE=config.settings.prod`.

- Config via **environment variables** (12-Factor). Use `pydantic-settings` (or `django-environ`) to parse/validate envs early; fail fast.
- Use **.env.example** + `Makefile` targets: `make up`, `make test`, `make fmt`, `make migrate`.

## 2. Security first

- Turn on `SecurityMiddleware`; set:
    - `SECURE_SSL_REDIRECT=True`, `SECURE_HSTS_SECONDS>=31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`, `SECURE_HSTS_PRELOAD=True`.

    - `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SESSION_COOKIE_SAMESITE='Lax'` (or `Strict` if possible).

- Use **CSP** via `django-csp`. Start in report-only; tighten over time.
- Prefer **Argon2** password hasher; enable Django password validators.
- Admin hygiene: move to `/admin-<hash>/`, enforce 2FA (e.g., `django-two-factor-auth`), staff-only IP allowlist on the reverse proxy, audit admin logs.
- Don’t trust the client: server-side authorization checks everywhere.

## 3. Apps, modules & boundaries

- Create small, focused **Django apps** with clear domain boundaries. Typical baseline:
    - `users`, `accounts` (billing/tenancy), `audit`, `notifications`, `api` (DRF), domain apps (e.g., `devices`, `events`, `analytics`).

- Keep **fat models, thin views**, and lift complex logic into **services** or **domain layer** modules (plain Python). Avoid putting business rules in views/serializers.
- Introduce **repository/query** modules for complex ORM reads; keep views from growing SQL vines.

## 4. Models & database

- Use **PostgreSQL**. For time-series, Postgres + **TimescaleDB** is excellent.
- Prefer **UUID primary keys** (`id = models.UUIDField(primary_key=True, default=uuid4, editable=False)`).
- Enforce integrity with **database constraints**:
    - `UniqueConstraint`, `CheckConstraint`, FK with `on_delete=PROTECT` (default to PROTECT; delete explicitly).

- Add **composite indexes** and `Index(..., condition=Q(...))` for partial indexes.
- Use **soft deletes** only if truly needed (and always filter by `alive` in managers).
- Avoid hidden `auto_now_add` traps for auditing; instead store immutable `created_at` and mutable `updated_at` with `auto_now=True` **and** DB triggers if you must guarantee correctness across paths.

### TimescaleDB (if doing time-series)

- Create **hypertables** on `(time, <partition_key>)`, set sane **chunk interval** (e.g., 1d/7d), **retention policies**, and **continuous aggregates** for rollups.
- Batch inserts; avoid per-row ORM writes in hot paths. Use `COPY`/`bulk_create` or an ingest service.

## 5. ORM patterns that scale

- Always profile queries; enable Django **query logging** in dev.
- Use `select_related` for FK, `prefetch_related` for M2M/Reverse FK; annotate to compute at DB layer.
- Avoid N+1s: enforce via tests or linters (e.g., custom assert “no more than N queries” for endpoints).
- Use `F()` expressions and `Case/When` for atomic updates; never read-modify-write in Python if you can do it in SQL.
- Keep long reports off the request path—use async tasks and cached materialized views.

## 6. APIs (DRF) & contracts

- Use **Django REST Framework** with:
    - ViewSets + routers (only where it maps well), else APIView.

    - Strict **serializers** (explicit fields), dataclasses/pydantic for nested business DTOs if helpful.

    - **Pagination** by default; never return unbounded lists.

    - **Validation**: DRF serializer validation + business validation in services (not in views).

    - **Versioning**: URL (`/api/v1/...`) or Accept header; never break V1 casually.

    - **Schema**: `drf-spectacular` to export OpenAPI; publish a docs UI.

    - **Auth**: session for web, **JWT (SimpleJWT)** or opaque tokens for API; rotate refresh tokens; add device-bound metadata.

    - **Rate limits**: DRF throttling or `django-ratelimit`. Distinguish user vs IP vs key-level.

- Return **problem details** (`application/problem+json`) for errors; include stable error codes.

## 7. Auth, users, permissions

- Start with a **custom User model** from day 0. Normalize emails; enforce uniqueness case-insensitively at DB.
- Use `permissions` at object and domain level; avoid ad-hoc “if staff” checks. For complex policies use a small **policy module** (ABAC style).
- For multi-tenant apps:
    - Decide **isolation model**: schema-per-tenant (`django-tenants`) vs **row-level** (tenant FK + `TenantMiddleware` + scoped managers).

    - Namespacing for cache keys per tenant; separate S3 buckets/prefixes for media if needed.

    - Migration strategy per tenant; protect cross-tenant data spills with DB constraints and tests.


## 8) Async, tasks & scheduling

- Run Django under **ASGI**; prefer **Uvicorn** (or Daphne for Channels).
- For background work: **Celery** + Redis/RabbitMQ. Best practices:
    - Tasks are **idempotent**, small, and retriable; use exponential backoff; set hard/soft time limits.

    - Pass **ids, not blobs**. Fetch inside the task.

    - Use a **unique task key** to avoid duplicates in hot paths.

    - Structured logging for tasks; export metrics (success/fail/latency).

- Real-time/websockets: **Django Channels** or an external pub/sub (e.g., NATS) with server-sent events.

## 9) Caching strategy

- Use `django-redis` as cache backend.
- Layered caching:
    1. **Per-view** (short TTL) for cheap list endpoints.

    2. **Low-level** cache around expensive computed values (keyed by inputs + tenant).

    3. **DB caching** (e.g., read-through for reference data).

- Invalidate on **writes**; don’t rely only on TTL. Encapsulate caching in service functions.

## 10) Static & media

- Small/simple deployment: **Whitenoise** for static.
- Production: push static to **S3/GCS** with `django-storages` + `ManifestStaticFilesStorage` (hashed filenames).
- Media: separate **public** and **private** storage; for private use signed URLs via the CDN/proxy.

## 11) Observability & operations

- **Logging**: JSON logs; include request id, user id, tenant id, correlation id. Propagate across Celery.
- **Tracing/metrics**: OpenTelemetry SDK + OTLP exporter; instrument Django, DRF, DB, Celery. Ship to Grafana Tempo/Jaeger; metrics to Prometheus (`django-prometheus`) and Grafana dashboards.
- **Errors**: Sentry (or equivalent) with release tagging and environment tagging.
- **Health**: `/healthz` (fast), `/readyz` (DB/cache checks). Use `django-health-check` or write your own.
- **Feature flags**: Open-source (e.g., Unleash) or a SaaS; never gate by `if env == 'prod'`.

## 12) Performance & capacity

- Put Django behind **nginx** (or Cloud Load Balancer) with HTTP/2, gzip/br.
- Use **connection pooling** (pgBouncer) for Postgres.
- Keep **requests < 200ms P95**; budget: view code ≤ 50ms, DB ≤ 100ms, everything else ≤ 50ms.
- Avoid synchronous outbound calls in request path; wrap in async with timeouts, circuit breakers (e.g., `httpx` + `pybreaker`).

## 13) Migrations without drama

- Ship schema changes in **safe steps**: add nullable column → backfill (async) → set default/non-null → swap code.
- Avoid destructive ops during peak; lock-aware operations; separate **data migrations** (idempotent, chunked).
- Keep migrations in CI; forbid squashing until a major release.

## 14) Testing strategy

- Use **pytest** + `pytest-django`, **factory_boy**, **faker**, **pytest-xdist** (parallel), **pytest-cov**.
- Pyramid of tests:
    - Unit (fast, isolated), service-layer tests,

    - API tests (contract + auth + pagination),

    - A small set of end-to-end smoke tests.

- Add **query count** assertions for hot endpoints.
- Seed data via factories, not fixtures. Make tests hermetic (ephemeral DB via `tmp_postgres` or Docker).

## 15) Tooling & quality gates

- Type checking: **mypy** (enable strict mode gradually), plus **django-stubs**.
- Linting/format: **ruff** (lint + isort), **black**. Enforce via **pre-commit**.
- Secrets scanning: `gitleaks` or `trufflehog`.
- Minimum coverage gate (e.g., 85%) with an exception process.

## 16) CI/CD & deployments

- CI: run linters, type checks, tests, migrations, build artifacts, generate OpenAPI schema, build container.
- CD: migrate DB **before** flipping traffic; collectstatic; warm caches; run smoke checks.
- Deployment patterns: **blue-green** or **canary**; add a simple **/version** endpoint and `X-Request-ID`.
- Containers: slim Python base, **multi-stage** build, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUNBUFFERED=1`, non-root user.
- Gunicorn (WSGI) for legacy, **Uvicorn workers** for ASGI. Configure worker count = `min(2, CPU)` to start; tune with load tests.
- Rollback plan: database backups + immutable images + migrations that roll forward only (use repair scripts for bad data).

## 17) Docs & governance

- Keep a living **README** + **/docs** with:
    - Architecture diagram, data model, API schema link, runbook (alerts → actions), release checklist, ADRs (Architecture Decision Records).

- Track **operational budgets** (SLOs, error budgets) and a quarterly **tech debt** cleanup list.

## 18) Internationalization, time & money

- `USE_TZ=True`, store UTC in DB; convert at edges. Never store local time.
- Use `Decimal` for money; centralize currency formatting and rounding. Store amounts + currency, not strings.


## 19) Data privacy & governance

- PII map: know which fields are sensitive; encrypt at rest where needed (`django-fernet-fields` or app-layer KMS).
- Add **data retention** jobs and right-to-erasure flows. Log all access to sensitive records.

---

## Minimal starter stack (pin these and go)

- Django 5.x, DRF, django-csp, django-redis, Celery, httpx, pydantic-settings, drf-spectacular, django-prometheus, Sentry SDK, mypy + django-stubs, ruff, black, pytest-django, factory-boy.

## Skeleton snippets

**Typed settings (pydantic-settings)**

```python
# src/config/typed_settings.py
from pydantic_settings import BaseSettings
from pydantic import AnyUrl

class Settings(BaseSettings):
    debug: bool = False
    secret_key: str
    database_url: AnyUrl
    redis_url: AnyUrl
    allowed_hosts: list[str] = ["example.com"]
    cors_origins: list[str] = []

    model_config = {"env_file": ".env", "env_prefix": "APP_"}

settings = Settings()
```

**Service boundary**

```python
# src/devices/services/register.py
from dataclasses import dataclass

@dataclass(frozen=True)
class DeviceInput:
    tenant_id: str
    serial: str
    label: str

def register_device(inp: DeviceInput) -> str:
    # validate, dedupe, persist (use repositories), emit domain events
    ...
```

**Celery config (idempotent tasks + backoff)**

```python
# src/config/celery.py
from celery import Celery

app = Celery("proj")
app.config_from_object({
    "broker_url": "...",
    "result_backend": "...",
    "task_acks_late": True,
    "task_default_retry_delay": 5,
    "task_routes": {"analytics.*": {"queue": "analytics"}},
})
```
