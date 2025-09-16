# Dev Checklist

## Architecture
- [ ] /docs/architecture/overview.md
  **Purpose:** One page with C4 L1 (context), L2 (containers), and **1** sequence (happy path).  
  **Done when:** boundaries + data flow are unambiguous in Mermaid diagrams.

## Interfaces
- [ ] /docs/api/api-contracts.md  
  **Purpose:** First endpoint(s), auth, error model; link to OpenAPI file.  
  **Done when:** one real request/response example + retry/backoff rules exist.

- [ ] /docs/api/event-contracts.md (if async)  
  **Purpose:** Topics, schema, ordering/idempotency, DLQ policy.  
  **Done when:** one event schema + producer/consumer noted.

## Engineering
- [ ] /docs/engineering/local-dev.md  
  **Purpose:** Local setup, env, seed data, run/stop, common gotchas.  
  **Done when:** a new dev can run the app and hit the health endpoint.

- [ ] /docs/engineering/standards.md  
  **Purpose:** Language versions, linters/formatters, commit/Git flow, branching, CI gates.  
  **Done when:** `lint`, `test`, and CI pass criteria are defined.

## Testing
- [ ] /docs/testing/strategy.md  
  **Purpose:** What to test in Sprint 1: unit/contract/e2e; how to run them.  
  **Done when:** smoke e2e for the main flow is specified.

## Decisions
- [ ] /docs/adrs/README.md + /docs/adrs/ADR-001-<platform-or-storage>.md  
  **Purpose:** Capture the first big choice (platform/storage/messaging).  
  **Done when:** context → options → choice → consequences recorded.

## Ops
- [ ] /docs/ops/observability.md  
  **Purpose:** What we log, trace correlation ID, 3 SLIs (latency, errors, saturation).  
  **Done when:** metric names and log fields are listed.

- [ ] /docs/ops/rollout.md  
  **Purpose:** Release, canary, and exact rollback steps (code + data).  
  **Done when:** a human can revert safely in 5 steps.

## Security (light but real)
- [ ] /docs/security/threat-checklist.md  
  **Purpose:** STRIDE-lite for MVP; authZ roles; secrets location.  
  **Done when:** top 5 threats + mitigations are named.

## Stories (link out, don’t duplicate)
- [ ] /docs/user-stories/<us>.md  
  **Purpose:** Key stories with acceptance criteria for Sprint 1.  
  **Done when:** at least one story maps to the happy-path sequence.
