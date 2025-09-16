# AI Agent Environment Guide

## Project Snapshot
- **Name:** [PROJECT_NAME]
- **Stack:** [TECH_STACK]
- **Key docs:** `README.md`, `docs/PRD.md`, `docs/PRODUCT_BACKLOG.md`, `docs/user-stories/`, `.x100/resources/references/TECHNICAL_GUIDELINE.md`

### Shared Tooling
- Docker compose services under `submodules/*/deploys/`
- Always ensure docs/ artifacts stay consistent (PRD → Backlog → Stories)

## Workflow for Agents

### Executing project tasks
1. **Understand context**
   Read PRD, Technical Guideline, relevant docs, and codebase.
3. **Plan output**
   For code, outline steps vs. acceptance criteria. For docs, adhere to templates in `.x100/resources/doc-templates/`.
4. **Execute**  
   Update relevant files; keep feedback loop short—commit small, complete units.
5. **Validate**  
   Run lint/test commands for touched areas. Update docs & telemetry checklists when needed.
6. **Document**  
   Update `docs/CHANGELOG.md`, `docs/PRODUCT_BACKLOG.md` and relevant docs.
