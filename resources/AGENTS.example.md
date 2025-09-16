# AI Agent Environment Guide

## Project Snapshot
- **Name:** gmbrew
- **Stack:** Next.js + pnpm frontend, Django backend, PostgreSQL + Redis
- **Key docs:** docs/IDEA.md, docs/REFINED_IDEA.md, docs/PRD.md, docs/PRODUCT_BACKLOG.md, docs/user-stories/
- **Agent notes:** Always sync with `.x100/config.json` and the latest docs before generating artifacts.

## Workspace Setup
### Frontend (Next.js)
1. `cd submodules/frontend`
2. `pnpm install`
3. `pnpm dev` to run Vite/Next dev server on http://localhost:3000
4. Useful jump command: `pnpm dlx turbo run where gmbrew-frontend`

### Backend (Django)
1. `cd submodules/backend`
2. `uv sync` (or `pip install -r requirements.txt` if uv unavailable)
3. `cp .env.example .env` and fill secrets
4. `python manage.py migrate`
5. `python manage.py runserver 0.0.0.0:8000`

### Shared Tooling
- Docker compose services under `submodules/*/deploys/`
- VS Code settings template at `.x100/resources/vscode/settings.example.json`
- Claude / Codex / Gemini command palettes inside `.x100/resources/claude|prompts`

## Testing & Quality Gates
- **Frontend:** `pnpm lint`, `pnpm test`, `pnpm vitest run -t "<name>"`
- **Backend:** `python manage.py test`, `ruff check`, `pytest` (if configured)
- **API Contracts:** verify against `docs/api/` OpenAPI specs
- Always ensure docs/ artifacts stay consistent (IDEA → PRD → Backlog → Stories)

## Workflow for Agents
1. **Understand context**  
   Read IDEA, REFINED_IDEA, PRD, Technical Guideline, SA Checklist.
2. **Pick task**  
   Reference `docs/user-stories/US-*.md` or sprint task checklist.
3. **Plan output**  
   For code, outline steps vs. acceptance criteria. For docs, adhere to templates in `.x100/resources/doc-templates/`.
4. **Execute**  
   Update relevant files; keep feedback loop short—commit small, complete units.
5. **Validate**  
   Run lint/test commands for touched areas. Update docs & telemetry checklists when needed.

## Pull Request Standards
- Title format: `[gmbrew] <Title>`
- Checklist before requesting review:
  - [ ] Lint and tests pass for affected packages (`pnpm lint --filter ...`, `pnpm test`, backend test suite)
  - [ ] Docs and templates updated when specs change
  - [ ] Linked user story / ticket noted in PR body
  - [ ] Screenshots or API samples included for UI/API changes
  - [ ] Rollback/feature-flag plan documented if relevant

## Troubleshooting Quick Links
- `.x100/resources/references/TECHNICAL_GUIDELINE.md`
- `.x100/resources/references/SA_CHECKLIST.md`
- `.x100/resources/prompts/` for prebuilt commands (idea→PRD, PRD→backlog, etc.)
- `.x100/scripts/check.py` for basic doc presence validation

Keep this file updated as the project evolves so every AI agent starts with the same shared context.
