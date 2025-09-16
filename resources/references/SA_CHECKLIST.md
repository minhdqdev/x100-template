# Solutions Architect Checklist
As a Solutions Architect, use this checklist to ensure the PRD and related documentation are complete and ready for review.

## Decisions
- [ ] /docs/adrs/README.md — ADR index
- [ ] /docs/adrs/ADR-<3_digits_numbers>-<decision>.md — first real decision
    - e.g., ADR-001-platform.md, ADR-002-storage.md

Use `.x100/doc-templates/ADR.md` as a template.

## Architecture (diagrams in Mermaid blocks)
- [ ] /docs/high-level-architecture.md — system context, key components, data flow
- [ ] /docs/diagrams/sequence-diagrams.md — key user/system interactions

## Data
- [ ] /docs/data/erd.md — core entities & relationships

## Interfaces (Markdown summaries that link to specs)
- [ ] /docs/api/api-contracts.md — endpoints, auth, error model, link to OpenAPI
- [ ] /docs/api/event-contracts.md — topics, schemas, ordering/idempotency, link to AsyncAPI

## Quality
- [ ] /docs/testing/test-plan.md — unit/contract/e2e/perf/security scope

## Ops
- [ ] /docs/ops/observability.md — logging, metrics, tracing, dashboards, alerts
- [ ] /docs/ops/deployment.md — CI/CD, environments, rollback, feature flags


