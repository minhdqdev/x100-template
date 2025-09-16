# Solutions Architect Checklist
As a Solutions Architect, use this checklist to ensure the PRD and related documentation are complete and ready for review.

## Decisions
- [ ] /docs/adrs/README.md — ADR index
- [ ] /docs/adrs/ADR-<3_digits_numbers>-<decision>.md — first real decision
    - e.g., ADR-001-platform.md, ADR-002-storage.md

Use `.x100/doc-templates/ADR.md` as a template.

## Architecture (diagrams in Mermaid blocks)
- [ ] /docs/diagrams/context.md — C4 L1 (system context)
- [ ] /docs/diagrams/containers.md — C4 L2 (containers + responsibilities)
- [ ] /docs/diagrams/sequence-happy.md — main happy path
- [ ] /docs/diagrams/sequence-failure.md — critical failure path

## Data
- [ ] /docs/data/erd.md — core entities & relationships
- [ ] /docs/data/classification.md — PII/sensitive classes; masking/retention

## Interfaces (Markdown summaries that link to specs)
- [ ] /docs/api/api-contracts.md — endpoints, auth, error model, link to OpenAPI
- [ ] /docs/api/event-contracts.md — topics, schemas, ordering/idempotency, link to AsyncAPI

## Ops & Quality
- [ ] /docs/ops/slos.md — SLO/SLI targets (latency, availability, errors)
- [ ] /docs/ops/alerts.md — alert rules & paging policy
- [ ] /docs/ops/runbooks.md — incident & rollback runbooks
- [ ] /docs/ops/rollout.md — release strategy (canary/blue-green) + exact rollback steps
- [ ] /docs/testing/test-plan.md — unit/contract/e2e/perf/security scope
