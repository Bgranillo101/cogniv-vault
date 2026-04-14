# Session Log

## 2026-04-13 — Phase 0 + Phase 1 scaffold

### Completed

- **Root config:** `.gitignore`, `.editorconfig`, `LICENSE` (MIT), `README.md`, `.nvmrc` (22), `.python-version` (3.12), `package.json`, `pnpm-workspace.yaml`, `CONTRIBUTING.md`.
- **Docs:** `docs/ARCHITECTURE.md` (Mermaid diagrams, agent loop, retry rule), `docs/API_CONTRACTS.md` (REST + WS event schema), `docs/DATA_MODEL.md` (Supabase + pgvector schema).
- **ADRs:**
  - `0001-monorepo-pnpm-workspaces`
  - `0002-python-tooling-uv`
  - `0003-embedding-model-minilm`
  - `0004-verification-threshold-0.8`
- **Backend (`/backend`):** uv project, `pyproject.toml` with FastAPI/LangGraph/Groq/Supabase/MiniLM deps, full package stubs (`api/`, `agents/`, `ingestion/`, `db/`), `main.py` app factory with CORS, `tests/test_health.py` passing, `Dockerfile`, `ruff.toml`, `.env.example`, `README.md`.
- **Frontend (`/frontend`):** Vite + React 19 + TS scaffold, Tailwind v4, Phaser 4, Zustand, TanStack Query. `BootScene` generates a placeholder pixel sprite; `LibraryScene` is arrow-key controllable (Phase 1 acceptance criterion met). Stubs for `api/client.ts`, `hooks/useAgentSocket.ts`, `stores/agentStore.ts`. Prettier + ESLint configured.
- **CI:** `.github/workflows/ci.yml` runs frontend (lint/typecheck/build) and backend (ruff/pytest) on PR + push to main.

### Verified locally

- `uv sync && uv run pytest` → 1 passed.
- `pnpm install` → 173 packages.
- `pnpm --filter frontend typecheck` → clean.
- `pnpm --filter frontend build` → builds (large chunk warning expected; Phaser is ~1.5 MB pre-split).

### Known rough edges

- **VS Code Python interpreter:** IDE flags missing packages until you point it at `backend/.venv/bin/python` (Command Palette → "Python: Select Interpreter"). uv's venv is correct; this is cosmetic.
- **Phaser 4 import style:** must be `import * as Phaser from 'phaser'` — no default export. Fixed across all scenes.
- **Frontend bundle size:** Phaser + React = ~1.5 MB. Code-split in Phase 5 when isometric assets land.
- **Backend mypy:** not yet run in CI (only `ruff` + `pytest`). Add once stubs become real code in Phase 2.
- **Ruff/mypy:** most `agents/` and `ingestion/` modules raise `NotImplementedError`; unused-arg warnings may surface once real logic lands.

### Not done (deferred to later phases)

- Supabase project provisioning + migrations (Phase 2)
- Real PDF chunking + MiniLM embedding pipeline (Phase 2)
- LangGraph graph wiring + Groq Llama-3-70B calls (Phase 3)
- Live WS event emission from agent nodes (Phase 4)
- Real sprites, isometric world, agent-state-driven animations (Phase 5)
- Vercel + Render deploy (Phase 6)

### Resume from here — next session

1. **Verify GitHub CI is green** on the first push.
2. **Start Phase 2 — ingestion pipeline:**
   - Provision Supabase project; apply schema from `docs/DATA_MODEL.md`.
   - Implement `ingestion/chunking.py` (pypdf + sliding window).
   - Implement `ingestion/embeddings.py` (MiniLM via `sentence-transformers`).
   - Wire `POST /api/v1/documents` to store + chunk + embed + insert.
   - Tests: fixture PDF → chunks persisted with correct dim.
3. Keep the frontend Phaser canvas; Phase 2 doesn't touch it.

### Environment snapshot

- Node `v24.12.0`, pnpm `10.0.0`
- Python `3.12` via uv, `uv 0.11.6`
- Repo: `/Users/bgranillo05/Documents/GitHub/cogniv-vault`
- Plan files:
  - `/Users/bgranillo05/.claude/plans/dazzling-wondering-cloud.md` (original)
  - `/Users/bgranillo05/.claude/plans/pure-zooming-wall.md` (resume plan, approved)
