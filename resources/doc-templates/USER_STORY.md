**Title:** <concise outcome>

As a <persona/role>,
I want <capability>,
so that <business value/benefit>.

**Context**
- Problem / motivation:
- Key users / personas:
- Assumptions / out of scope:

**Acceptance Criteria (testable)**
- [Given ... When ... Then ...]
- [Given ... When ... Then ...]
- Edge cases: <list>

**Non-Functional / Constraints:**
- Performance: <e.g., P95 < 300ms>
- Security/Privacy: <e.g., PII masked, GDPR>
- Accessibility: <e.g., WCAG 2.1 AA>
- Reliability: <e.g., 99.9% monthly>
- Compliance/Localization: <if applicable>

**Dependencies:**
- <systems, teams, feature flags, data>

**Tasks:**
- [ ] T0001 - Spike: clarify unknowns / update AC (Owner: <name>, Effort: S)
- [ ] T0002 - API contract drafted and reviewed (Type: BE, Link: <spec>)
- [ ] T0003 - Backend: implement endpoint <verb> /v1/<resource> (Type: BE, Effort: M)
- [ ] T0004 - Backend: unit + integration tests (Type: BE/QA)
- [ ] T0005 - Frontend: UI for <flow/screen> incl. validation (Type: FE, Effort: M)
- [ ] T0006 - Frontend: state management + API wiring (Type: FE)
- [ ] T0007 - UX copy, empty/edge states, error handling (Type: Design/FE)
- [ ] T0008 - Telemetry: events + dashboards/alerts (Type: Ops/FE/BE)
- [ ] T0009 - Security review / threat modeling (Type: Sec)
- [ ] T0010 - Docs: user help, API docs, release notes (Type: Docs)
- [ ] T0011 - Launch: feature flag rollout plan + toggle default (Type: Ops/PM)
- [ ] T0012 - Post-release checks: logs, metrics, bug triage (Type: PM/Eng)

**Tracking:**
- Priority: <Must/Should/Could> or <P1–P4>
- Story points / size: <n>
- Epic / link: <id>
- Definition of Done:
  - [ ] All AC pass (automated where possible)
  - [ ] Code reviewed & merged
  - [ ] Feature flagged (default off/on decided)
  - [ ] Security/privacy checks complete
  - [ ] Monitoring/alerts in place; dashboards updated
  - [ ] Docs/help & analytics updated

**Comments:**
