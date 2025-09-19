# Technical Guideline

## 1. Purpose
This guideline helps SA and DEV choose consistent defaults for software product. Unless a documented exception exists, follow these recommendations to achieve maintainable systems and predictable operations. Record any deviation in an ADR that explains the trade-offs and approval.

## 2. Architectural Principles
- Start simple: favour modular monolith or service-oriented designs before introducing microservices or event-driven architecture.
- Make domain boundaries explicit through well-defined modules, APIs, and shared contracts.
- Prefer convention over configuration: adopt mature frameworks and tooling rather than bespoke glue code.
- Automate from the outset: tests, packaging, deployment, and quality checks run in CI/CD for every change.
- Keep documentation and diagrams versioned with the codebase; update them as part of feature work.

## 3. Codebase Management
### 3.1 Repository layout
- Default: manage backend and frontend as Git submodules under `submodules/backend/` and `submodules/frontend/` to allow independent release cadences while keeping the integration repo slim.
- Alternative: a monorepo is acceptable when both stacks share release cadence and tooling; document the rationale in an ADR and ensure build pipelines remain isolated per component.
- Avoid mixing unrelated prototypes or throwaway code inside production repositories.

### 3.2 Collaboration practices
- Use trunk-based development or short-lived feature branches with mandatory reviews and automated checks.
- Run the full test suite and static analysis in CI for every merge request across all submodules.
- Tag releases and maintain change logs so operational teams can trace deployments back to commits.

### 3.3. Dependency management
#### Django/Python
- Use `uv` to manage dependencies and generate lock files (`uv lock`).


### 3.4. Package management
#### Django/Python
- Django app should be named `core` to avoid conflicts with third-party packages. Avoid creating multiple Django apps unless there is a clear modularity or reuse benefit.
- Every module should have docstrings and type annotations (PEP 484).
- Follow PEP 8 for code style; use `black` for formatting and `flake8` for linting.
- Group related functionality into submodules under `core/`, e.g., `core/models/`, `core/views/`, `core/services/`, `core/utils/`.
- Each submodule should have an `__init__.py` file to mark it as a package.
- Models should be defined in `core/models.py` or `core/models/` if complex.
- Views should be in `core/views.py` or `core/views/` if complex.
- Serializers should be in `core/serializers.py` or `core/serializers/` if complex.
- Utility functions should be in `core/utils.py` or `core/utils/` if complex.
- Avoid deeply nested packages; flatten the structure when possible to reduce import complexity.
- Use relative imports for intra-package references and absolute imports for external packages.
- Service modules should include header docstrings explaining their purpose and usage.
- Service modules should be put under `core/services/` with a `__init__.py` file to mark it as a package. `services/__init__.py` should import submodules to expose a clean public API, for example:

```python
from .brew_service import BrewService
from .digest_service import DigestService

__all__ = [
    "BrewService",
    "DigestService",
]
```

## 4. Default Technology Stack
### 4.1 Backend
- Language: Python 3.12+ is the default because of the team skillset, ecosystem maturity, and excellent Django support.
- Framework: Django is preferred for its batteries-included ORM, admin, and security hardening. Consider FastAPI only for lightweight APIs that do not need Django’s features.
- Dependency management: use `uv` to guarantee reproducible lock files, deterministic builds, and rapid installs.
- Application server: run behind `uvicorn` for ASGI support and async capabilities. Reserve alternatives (e.g., Gunicorn, Hypercorn) for platform constraints that block `uvicorn`.
- Caching: use Redis for in-memory caching and rate limiting.
- Task queue: use Celery with Redis as the broker for background jobs.
- Messaging: use RabbitMQ or Redis streams for inter-service communication when needed. For complicated workflows, consider Apache Kafka.
- Testing: write unit tests with `pytest` and `pytest-django`, use `factory_boy` for test data, and run integration tests with `pytest` or `requests`. Include linting (flake8, black) and type checking (mypy) in CI.
- Data access: use Django’s ORM with repository abstractions when cross-service reuse is required. Only use raw SQL when justified by performance or complex queries.
- Observability: ship structured logs (JSON), capture OpenTelemetry traces, and expose Prometheus metrics by default.

Refer to the `./DJANGO.md` file for best practices specific to Django projects.

### 4.2 Frontend
- Framework: Next.js with React 18+ and TypeScript provides server-side rendering, routing, and strong DX.
- Styling: use a design system or component library agreed by the product team; document deviations.
- Testing: add unit tests (Vitest/Jest), integration tests (Playwright/Cypress), and linting (ESLint) to CI.

Refer to the `./NEXTJS.md` file for best practices specific to Next.js projects.

### 4.3 Data stores and messaging
- Primary datastore: PostgreSQL is the standard for relational workloads because of reliability, migrations, and first-class Django support. Choose managed instances (e.g., RDS) whenever possible.
- Secondary stores: introduce MySQL or other relational databases only when a hosting constraint prevents PostgreSQL.
- NoSQL: adopt MongoDB or DynamoDB for document/large-scale workloads with clearly justified access patterns. Document read/write volume, consistency requirements, and retention policy before adoption.
- Caching & queues: Redis is the default cache and message broker. Use Celery or RQ for background jobs; consider cloud-native alternatives (SQS, Pub/Sub) only when integrating with cloud-managed ecosystems.

### 4.4 Infrastructure
- Containerisation: package services with Docker. Provide reproducible `Dockerfile`s checked into each submodule.
- Orchestration: use Docker Compose for local development and integration testing. Move to Kubernetes or managed container services when scale, resilience, or multi-service deployments require it; capture the transition in an ADR.

## 5. API Design
- Document every external API with OpenAPI 3.x and publish generated docs alongside the service.
- Version APIs explicitly (`/api/v1/...`) and deprecate old versions with clear timelines.
- Follow REST conventions: nouns in URLs, appropriate HTTP verbs, HATEOAS when helpful.
- Standardise error responses with machine-readable codes, human-readable messages, and trace IDs.
- Provide pagination, filtering, and sorting for collection endpoints. Define rate limits and idempotency expectations.
- Include example requests/responses and authentication expectations in the OpenAPI spec.

## 6. Data Management
- Table names should be singular and lowercase with underscores (e.g., `user_profile`).
- Manage schema changes with migrations committed to source control; one migration per logical change.
- Apply retention policies, archival plans, and GDPR-compliant deletion workflows.
- Encrypt sensitive data at rest and in transit. Use application-level encryption for fields that require it.
- Establish backup schedules, test restores quarterly, and document RPO/RTO targets.

## Testing
- Write unit tests for all business logic, aiming for >80% coverage.
- Use integration tests to cover critical workflows and edge cases.
- Run tests in isolated environments with a fresh database state for each run.
- Use `pyproject.toml` as the single configuration file for `pytest` other than the old `pytest.ini`.

## 7. Security
- Enforce HTTPS everywhere; redirect HTTP to HTTPS automatically.
- Authenticate APIs with bearer tokens (JWT or opaque tokens) and authorise with least-privilege roles.
- Store credentials and secrets in a dedicated secret manager (e.g., Vault, AWS Secrets Manager); never commit them to git.
- Run SAST, dependency vulnerability scanning, and container image scanning in CI.
- Apply secure coding guidelines (OWASP ASVS) and threat-model significant features. Document mitigations.

## 8. Performance & Resilience
- Implement caching strategies (Redis, CDN) for frequent reads, with explicit cache invalidation rules.
- Offload long-running work to asynchronous workers or event-driven pipelines.
- Define performance budgets and SLIs/SLOs; test them via load/chaos testing prior to launch.
- Instrument code with metrics, traces, and logs; aggregate them in a central observability stack.
- Use circuit breakers, retries with exponential backoff, and timeouts when calling external services.

## 9. Deployment & Operations
- Build immutable images with Docker; pin versions of base images and dependencies.
- Use GitHub Actions or GitLab CI/CD pipelines for automated builds, tests, security scans, and deployments.
- Roll out changes with canary or blue/green deployments when production impact is high; otherwise use rolling updates.
- Manage configuration via environment variables injected at deploy time; keep environment parity across dev/staging/prod.
- Maintain runbooks, incident response checklists, and rollback procedures stored alongside the service.

## 10. Governance and Decision Records
- Capture architectural decisions in ADRs within `docs/adrs/`; link them from relevant sections of this guideline.
- Review this guideline quarterly to ensure technology choices remain current.
- Provide onboarding notes and diagrams (`docs/diagrams/`, `docs/data/`) that reflect the latest state before major releases.
