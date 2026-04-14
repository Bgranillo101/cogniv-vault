# Session Log

## 2026-04-14 — Phase 2 ingestion pipeline

### Completed

- **Schema migration:** `backend/migrations/0001_init.sql` mirrors `docs/DATA_MODEL.md` — `vector`/`pgcrypto` extensions, `documents` and `chunks` tables, `vector(384)` column, ivfflat cosine index (`lists=100`), and `chunks(document_id)` btree. Designed to be pasted into the Supabase SQL editor once per environment.
- **Embeddings (`ingestion/embeddings.py`):** `@lru_cache` MiniLM singleton; `embed()` returns 384-dim L2-normalized vectors via `normalize_embeddings=True` so cosine distance ≡ dot product in pgvector. `EMBEDDING_DIM = 384` exposed as a constant.
- **Chunking (`ingestion/chunking.py`):** tokenizer-aware 220/32 windowing using MiniLM's own `AutoTokenizer`. Stays below the 256-token cap (leaves headroom for `[CLS]`/`[SEP]`). Returns a list of `Chunk` TypedDicts with `ordinal`, `content`, `token_count`. Handles empty input and sub-window text correctly.
- **PDF parse (`ingestion/pdf.py`):** `extract_text(bytes) -> (text, page_count)` via pypdf, joining pages with `\n\n`, raising `ValueError` on zero-page PDFs.
- **Error envelope (`api/errors.py`):** uniform `{error: {code, message, detail?}}` JSON response helper per `docs/API_CONTRACTS.md`. Adopted by `documents.py`; `query.py` / `ws.py` will pick it up in Phase 3.
- **Documents API (`api/documents.py`):** end-to-end wiring.
  - `POST /api/v1/documents`: validate content-type (`application/pdf`, 415 otherwise) and size (≤ 25 MB, 413 otherwise) → extract text → insert `documents` row with `status=processing` → chunk → embed in batches of 32 → bulk `insert` into `chunks` → flip to `status=ready`. On exception, flips to `status=failed` and returns 500 via the error envelope. Returns **202** `{document_id, filename, status: "queued"}` to match the API contract even though Phase 2 processes synchronously.
  - `GET /api/v1/documents`: single query via Supabase's embedded-resource count (`chunks(count)`), ordered `uploaded_at desc`.
  - Work done in a thread (`asyncio.to_thread`) so the blocking Supabase client doesn't stall the event loop.
- **db/client.py:** return type tightened from `object` to `supabase.Client` — clean under `mypy --strict`.
- **Tests (8 new):**
  - `test_chunking.py` — empty input → `[]`; short input → single chunk; long input → contiguous ordinals starting at 0, every chunk ≤ 220 tokens.
  - `test_embeddings.py` — empty batch → `[]`; single vector shape 384 with L2 norm ≈ 1.0; batch of 3 returns 3×384.
  - `test_documents_api.py` — fake Supabase client + monkeypatched `extract_text` / `chunk_text` / `embed`; happy path asserts 202 + document row with `status=ready` + N chunk rows with 384-dim embeddings; rejection path asserts 415 + `unsupported_media_type` envelope.
- **Editable-install chore:** formally accepted the `uvicorn --app-dir src ...` convention as the Phase 2 answer to the hatchling / `_virtualenv.pth` ordering bug. Documented in `README.md`. Revisit only if a contributor trips on it.
- **Dep bump:** `transformers>=4.44` added explicitly to `backend/pyproject.toml` since `ingestion/chunking.py` imports `AutoTokenizer` directly (previously pulled in transitively via `sentence-transformers`).

### Verified locally

- `uv run pytest` → **9 passed** in ~16 s (first run ~40 s on cold model cache).
- `uv run ruff check .` → clean.
- `uv run mypy src` → clean under `strict = true`.

### Known rough edges

- Editable-install workaround (`uvicorn --app-dir src ...`) still required — accepted for Phase 2.
- **Security:** the Supabase `service_role` key was pasted in chat during Phase 1 wiring. Rotate via dashboard → Project Settings → API Keys → service_role → Reset, then update `backend/.env`.
- MiniLM model + tokenizer download (~90 MB + a few MB) happens on the first test run; CI will re-download on every job until a HuggingFace cache step is added.
- `GET /documents` uses PostgREST embedded-resource count — relies on the FK from `chunks.document_id → documents.id` that the migration defines. Don't drop the FK without updating the query.

### Not done (deferred)

- Phase 3: Librarian/Analyst/Auditor wired to Groq; retry-on-low-score routing; LangGraph state machine.
- Phase 4: real WebSocket event emission from agent nodes.
- Phase 5: sprite art + agent-state-driven animations.
- Phase 6: Vercel + Render deploy.

### Resume from here — next session

1. **Rotate Supabase service_role key** and update `backend/.env` (security hygiene).
2. **Apply `backend/migrations/0001_init.sql`** in the Supabase SQL editor (one-time per environment).
3. **Live-ingest smoke test:** backend running, `curl -F 'file=@some.pdf' http://localhost:8000/api/v1/documents` → 202; confirm a row in `documents` (`status=ready`) and N rows in `chunks` with 384-dim embeddings.
4. **Begin Phase 3:** wire the agent loop — Groq client, Librarian similarity search via pgvector (`select ... order by embedding <=> $1 limit 5`), Analyst draft, Auditor score, retry on `score < 0.8` with `max_attempts = 3`.

### Environment snapshot

- Node `v24.12.0`, pnpm `10.0.0`
- Python `3.12` via uv, `uv 0.11.6`
- Repo: `/Users/bgranillo05/Documents/GitHub/cogniv-vault`
- Plan files:
  - `/Users/bgranillo05/.claude/plans/pure-zooming-wall.md` (Phase 2, approved)

---

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
