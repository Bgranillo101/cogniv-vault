# Session Log

## 2026-04-14 — Phase 3 agent loop

### Completed

- **Migration `0002_match_chunks.sql`:** pgvector cosine RPC. Takes a `vector(384)` query embedding, optional `uuid[]` document filter, and `match_count`; returns `(chunk_id, document_id, ordinal, content, similarity)` ordered by `embedding <=> query_embedding`. Stable, callable via Supabase `client.rpc("match_chunks", …)`.
- **Groq wrapper (`llm/groq_client.py`):** `@lru_cache` singleton + one `async chat(messages, *, model, temperature, response_format)` helper that delegates to `asyncio.to_thread` around the sync Groq client. Reads `GROQ_MODEL` from settings; defaults to `llama-3.3-70b-versatile`.
- **Config + env:** `Settings` gains `top_k=5`, `groq_model="llama-3.3-70b-versatile"`. `.env.example` gets both.
- **Prompts (`agents/prompts.py`):** centralized Analyst and Auditor system prompts + `build_*_messages` helpers that number the retrieved excerpts. Keeps node logic slim.
- **Nodes wired:**
  - `librarian.py` — embeds `refined_query or question`, calls the `match_chunks` RPC, shapes results into `Hit` TypedDicts.
  - `analyst.py` — calls Groq at `temperature=0.2` with the numbered-excerpt prompt, stores `state["draft"]`.
  - `auditor.py` — calls Groq with `response_format={"type": "json_object"}` and `temperature=0.0`, parses the JSON, clamps `score` to `[0, 1]`, propagates `refined_query` only if non-empty.
- **Graph (`agents/graph.py`):** real `StateGraph(AgentState)` with nodes `librarian → analyst → auditor → (finalize | bump_attempt)`. Conditional edge exits to `finalize` if `score >= threshold` OR `attempt >= max_attempts`, else `bump_attempt` increments the counter and loops back to `librarian`. `finalize` writes `answer`/`low_confidence`/`citations`. Graph is memoized via `@lru_cache`.
- **Runner (`agents/runner.py`):** wraps `build_graph().ainvoke()` with initial state seeding (`attempt=1`, `threshold`, `max_attempts`, `started_at`). Shapes terminal output to the `AGENT_RESULT` contract: `{answer, confidence, low_confidence, citations[{chunk_id, document_id, snippet}], trace{attempts, final_score, duration_ms}}`.
- **Job store (`agents/job_store.py`):** thread-safe TTL-LRU dict (5-min expiry, 100-entry cap). Process-local, in-memory only — documented as lost-on-restart. Placeholder until Phase 4 swaps the poll for a WebSocket stream.
- **Query API (`api/query.py`):** `POST /query` validates non-empty question, runs the graph synchronously, stores the result under a fresh UUID, returns `202 {job_id}`. `GET /query/{job_id}` pops the stored result (one-shot) or returns 404 via the error envelope. Agent-side exceptions caught and returned as `500 agent_failed`.
- **Frontend:** new `QueryPanel.tsx` — input + submit, fires `submitQuery → getQueryResult`, renders answer, confidence, attempts, duration, and collapsible citations. Mounted above the existing Phaser canvas in `App.tsx`. `api/client.ts` gained `getQueryResult` + exported `QueryResult`/`Citation` types.
- **Tests (5 new, 14 total):**
  - `conftest.py` — `fake_groq` fixture queues scripted responses and monkeypatches `chat` at all three import sites (analyst, auditor, module). `fake_supabase_rpc` monkeypatches `get_supabase_client` + `embed` in the librarian module and returns canned hits.
  - `test_agents_graph.py` — single-pass success (score 0.92 → attempt=1, low_confidence=False, citations populated), retry-then-success (0.5 → 0.85, attempt=2, refined_query carried), hard fail (0.3 × 3 → attempt=3, low_confidence=True, draft still surfaced).
  - `test_query_api.py` — POST → GET round-trip returns the AGENT_RESULT payload; second GET is 404 (one-shot eviction); empty question is 400 `invalid_request`.
- **Docs:** ADR 0005 (Groq model + JSON-mode for auditor). README status + "What works today" matrix + quickstart updated with `GET /query/{job_id}` example and the 0002 migration step.

### Verified locally

- `uv run --active pytest` → **14 passed** in ~9 s.
- `uv run --active ruff check .` → clean.
- `uv run --active mypy src` → clean under `strict = true`.
- `pnpm --filter frontend typecheck` + `lint` → clean.

### Known rough edges

- **Editable-install workaround still required** — `uv run --active` (or `uvicorn --app-dir src …`) is how the package is importable. Unchanged from Phase 2.
- **Job store is in-memory only.** Backend restart drops all pending results; fine for Phase 3 since there is no production deploy. Phase 4's WS removes the need for this store.
- **No general-knowledge fallback yet.** Ungrounded questions (nothing relevant in the library) will surface as low-confidence answers — by design. A `router` node for ungrounded fallback is scoped as a Phase 7+ add-on.
- **Only PDFs still.** Other upload formats (markdown, HTML, images/OCR) remain Phase 7+ work; the pipeline downstream of `extract_text()` is already format-agnostic.
- **Groq model is pinned via env.** Changing `GROQ_MODEL` works, but Auditor scoring calibration should be re-validated before promoting a new model.

### Not done (deferred)

- Phase 4: WebSocket emission of per-node events (`AGENT_START`, `AGENT_SEARCH`, `AGENT_SYNTHESIZE`, `AGENT_VERIFY`, `AGENT_RETRY`, `AGENT_RESULT`).
- Phase 5: Phaser sprites + agent-state-driven animations keyed off WS events.
- Phase 6: Vercel + Render deploy.
- Phase 7+: ungrounded-query fallback path, additional upload formats.

### Resume from here — next session

1. **Apply `backend/migrations/0002_match_chunks.sql`** in the Supabase SQL editor (one-time per environment). Verify: `select match_chunks(array_fill(0::real, array[384])::vector(384), 1);` runs without error.
2. **Rotate Supabase `service_role` key** (still pending from Phase 2 — was pasted in chat during Phase 1 wiring).
3. **Live end-to-end smoke test:** ingest a PDF → `curl -X POST http://localhost:8000/api/v1/query -H 'content-type: application/json' -d '{"question":"…"}'` → 202 → `curl /api/v1/query/<job_id>` → real answer + citations from your content.
4. **Begin Phase 4:** emit per-node events over `/ws/query/{job_id}`. Shape matches `docs/API_CONTRACTS.md`. Source events from within each agent node (callback / queue-per-job pattern), drop the poll, keep `GET /query/{job_id}` as a replay endpoint.

### Environment snapshot

- Node `v24.12.0`, pnpm `10.0.0`
- Python `3.12` via uv, `uv 0.11.6`
- Repo: `/Users/bgranillo05/Documents/GitHub/cogniv-vault`
- Plan files:
  - `/Users/bgranillo05/.claude/plans/phase-3-agent-loop.md` (approved, executed)

---

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
