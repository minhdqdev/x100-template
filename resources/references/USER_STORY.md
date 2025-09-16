# User Story Writing Best Practices
This document outlines best practices for writing effective user stories that drive development and ensure alignment with user needs.

**1. Lead with value, not tasks**
Write from the user’s perspective and outcome: “so that <benefit>”. If you can’t finish that clause, it’s not a story—it's a task.

**2. Keep them small and vertical**
Slice front-to-back increments that are demoable. Avoid “UI only” or “backend only” stories unless it’s a spike.

**3. Apply INVEST**
Independent, Negotiable, Valuable, Estimable, Small, Testable. If one letter fails, refine.

**4. Acceptance Criteria = binary checks**
Use Given/When/Then. Each AC should be unambiguous, pass/fail, and independent. Include edge cases.

**5. Make assumptions explicit**
List constraints, out-of-scope items, and risky dependencies to reduce hidden work.

**6. Bake in non-functionals**
Performance, security, privacy, accessibility, reliability—attach concrete thresholds (e.g., “P95 < 300ms”, “WCAG 2.1 AA”).

**7. Prefer concrete examples**
Examples beat adjectives. Replace “fast” with exact timing; “secure” with specific controls.

**8. One outcome per story**
If the title needs “and”, split it. Cohesion > kitchen-sink.

**9. Feature-flag and measure**
Include rollout/rollback plan and telemetry in tasks. Define the key event you’ll track to prove value.

**10. Use ‘3 Amigos’ refinement**
Product, dev, and QA walk the story together before sprint. Catch ambiguity early.

**11. Definition of Ready / Done gates**
DoR: user, value, AC, dependencies clear, small enough.
DoD: tests pass, docs updated, monitoring/alerts in place, flag strategy decided.

**12. Avoid solution bias (at first)**
Describe capability, not implementation. Add technical notes later in tasks.

**13. Map to personas and journeys**
Tie stories to a real persona and step in the flow; prevents orphan features.

**14. Timebox spikes**
Unknowns? Write a spike story with explicit questions and decision outputs.

**15. Keep language plain**
No jargon, no passive voice. If a stakeholder can’t read it, you’re writing specs, not stories.

---

### Example (compact)

**Title:** Save dashboard filters
**Story:** As a power user, I want my dashboard filters to persist across sessions so that I don’t reconfigure them every time.
**AC:**

* Given I apply filters A,B, when I reload, then the same filters are active.
* Given I switch devices while logged in, when I open the dashboard, then last used filters load in <200ms after paint.
* Given private browsing, when I reload, then filters do not persist.
