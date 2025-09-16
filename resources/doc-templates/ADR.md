# ADR-000: <Short, imperative title>

- **Status:** Proposed | Accepted | Rejected | Superseded by ADR-###
- **Date:** YYYY-MM-DD
- **Owners:** <name(s)>
- **Reviewers/Approvers:** <name(s)>
- **Related:** PRD §__, Epic/Issue #__, RFC #__

## 1) Decision (one sentence)
<What are we doing and at what boundary?>

## 2) Context (problem & constraints)
- Problem statement:
- Business/PRD drivers:
- Constraints (time, budget, tech, compliance, data residency):
- Assumptions:

## 3) Decision drivers (rank or bullets)
- <e.g., p95 latency ≤ __ms>
- <e.g., minimize vendor lock-in>
- <e.g., simple rollback>

## 4) Options considered
### Option A — <name>
- Summary:
- **Pros:**
- **Cons:**
- Risks:
- Known adopters/references:

### Option B — <name>
- Summary:
- **Pros:**
- **Cons:**
- Risks:
- Known adopters/references:

### Option C — <name>
- …

## 5) Chosen option
- **Choice:** <Option X>
- **Why this over others:** <key rationale tied to drivers>

## 6) Consequences
- **Positive:** <benefits, capabilities unlocked>
- **Negative:** <trade-offs, complexities introduced>
- **Neutral/Unknowns:** <what we’ll learn>

## 7) NFR & compliance impact
- Performance: target p95 __ms, throughput __/s
- Availability: __% (SLO), RTO __, RPO __
- Security/Privacy: authZ model, data classes touched (PII?); mitigations
- Reliability/Resilience: retries, timeouts, idempotency, fallbacks
- Maintainability/Operability: ownership, blast radius
- Cost/FinOps: est. $__/month or $__/tx; ceiling __
- Compliance: GDPR | VN PDPD | PCI DSS | HIPAA | other: __

## 8) Rollout & ops plan
- Migration/Backfill steps:
- Feature flag / canary / blue-green:
- Observability: metrics, alerts, dashboards
- Runbooks & rollback plan:

## 9) Alternatives rejected (brief)
- <Option/idea> — <1–2 line reason>
- <Option/idea> — <reason>

## 10) Follow-ups & owners
- [ ] Task — Owner — Due
- [ ] Task — Owner — Due

## 11) Links & attachments
- Diagrams (C4/sequence), OpenAPI/AsyncAPI, POCs, benchmarks, notes

---
**Changelog:**  
- YYYY-MM-DD: <change> (status update / superseded / amendments)
