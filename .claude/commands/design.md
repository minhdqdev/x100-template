---
description: Generate design documents
model: opus
---

- Use `solutions-architect` subagent to generate design documents for the product
- Only overwrite existing docs if $ARGUMENTS is "force"
- If `docs/PRD.md` does not exists, just stop and ask me to create it first with command `/gen-prd`.

References:
- `docs/PRD.md`
- `doc-templates/DESIGN_CHECKLIST.md`
- `references/COMPANY_TECH_DESIGN.md`
