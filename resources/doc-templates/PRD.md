# Product Requirements Document (SA-Ready)

## 1. Overview
**Context:**  
**Proposed solution:**  
**Differentiation / why now:**

## 2. Goals & Non-Goals
**Primary outcome:**  
**Key success metrics (KPIs):**  
- Metric 1: definition + data source
- Metric 2: definition + data source  
**Non-goals / out of scope:**

## 3. Users & Stories
**Target users / early adopters:**  
**User stories:** in `docs/user-stories/`  
- Mark **architecturally significant** stories with `ASR:` and include acceptance criteria.

## 4. Scope
**Must-have (MVP):**  
- [ ]  
**Nice-to-have (Future):**  
- [ ]  
**Anti-features (explicitly NOT doing):**  
- [ ]

## 5. Requirements
**Functional (what it should do):**  
- [ ]  
- [ ]  
- [ ]  

**Non-functional (constraints):**  
- Platform support: ☐ mobile web ☐ desktop ☐ APIs  
- Security: ☐ SSO/OIDC ☐ MFA ☐ RBAC  
- Privacy & data residency: __  
- Performance & capacity: target RPS __, p95 latency __ms, max objects/day __  
- Availability & resilience: target __%, RTO __, RPO __  
- Cost ceiling / unit economics: __/MAU or __/tx

## 6. Architecture Drivers
- Business constraints: __
- Quality attribute priorities (rank): performance, availability, security, cost, maintainability, portability (edit order)
- Compliance: ☐ GDPR ☐ PDPA (SG) ☐ VN PDPD ☐ PCI DSS ☐ HIPAA ☐ other: __

## 7. System Architecture (C4)
- **Context (L1):** link diagram
- **Containers (L2):** services + responsibilities
- **Components (L3):** key modules, boundaries
- **Deployment view:** regions, envs (dev/stg/prod), tenancy model, infra as code link

## 8. Data Model & Lifecycle
- Core entities & relationships (ERD link)
- Data classification: ☐ Public ☐ Internal ☐ PII ☐ Sensitive
- Retention & deletion: __; legal holds: __
- Backups & recovery: schedule __; encryption at rest ☐; keys in __

## 9. Interfaces & Integrations
- **Inbound APIs:** versioning, auth, rate limits, error model
- **Outbound calls:** systems, SLAs, timeouts, retries, circuit breakers
- **Events/Queues:** topics, schemas, ordering/idempotency policy, DLQ
- **Data contracts:** schema registry link; change policy

## 10. Capacity, Performance & Resilience
- Traffic model: peak RPS __, concurrency __, data size/day __
- Scaling strategy: ☐ HPA ☐ shards ☐ partitions; backpressure strategy: __
- Availability design: redundancy zones __; graceful degradation plan
- DR: active-active/active-passive; failover steps; RTO/RPO targets

## 11. Security & Threat Model
- AuthN/AuthZ: OIDC provider, roles/permissions
- Secrets: storage __; rotation policy __
- Threats & mitigations (STRIDE summary): __
- Audit logging requirements: __

## 12. Observability & Ops
- Metrics (SLIs): latency, availability, saturation, errors
- Dashboards/alerts: links; paging policy & runbooks
- Logging/tracing: correlation IDs, retention
- Feature flags & config strategy; migration/backfill plan

## 13. Testing & Quality
- Test strategy: unit / contract / e2e / performance / security / chaos
- Staging parity & test data mgmt
- Acceptance criteria linkage to stories

## 14. Rollout & Change Management
- Release plan: ☐ canary ☐ blue-green ☐ feature flags
- Rollback triggers & procedure
- Versioning & deprecation policy
- Migration steps (schema, data, clients)

## 15. Risks, Assumptions, Decisions
- **Assumptions to validate:**  
- **Top risks & mitigations:**  
- **ADR index:** `/docs/adrs/` (1-line per decision: context → choice → consequence)

## 16. Timeline & Milestones
- MVP target date: __
- Milestone 2: __ (e.g., first 100 users, investor demo)
- Critical path & dependencies: __

## 17. Open Questions & Owner
- Q1: __ (Owner: __, Due: __)
- Q2: __ (Owner: __, Due: __)

## 18. Appendices
- Glossary, references, Figma, runbooks, IaC repo, OKR link


## 19. One-Pager (for Solutions Architect)
- Problem & outcome (2–3 lines):
- Architecturally Significant Requirements (ASRs): ☐ scale ☐ security ☐ data integrity ☐ low latency ☐ compliance ☐ cost
- NFR targets (SLO/SLI): p95 latency __ms | availability __% | error rate __% | throughput __/s | durability __ | RTO __ | RPO __
- Constraints (hard): budget __, time __, tech/infra __, data residency __
- Go/No-Go criteria for MVP:
