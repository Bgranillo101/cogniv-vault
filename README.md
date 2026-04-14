# Cogniv-Vault

> An **observable agentic RAG system** — a Librarian → Analyst → Auditor agent loop that ingests documents, answers queries, and streams its internal state to a **Phaser.js pixel-art visualization** in real time.

Most RAG systems are black boxes: you submit a question, wait, and receive an answer. Cogniv-Vault treats the agent pipeline as a first-class observability surface — every retrieval, draft, and verification step becomes an event that the UI renders as animated agents working inside a tiny library. You don't just see the answer; you see *how the machine got there.*

---

## Status

**Phase 2 complete — ingestion pipeline is live.** You can `POST` a PDF to the backend and it is parsed (pypdf), chunked (MiniLM-tokenizer-aware, 220 tokens / 32 overlap), embedded locally (`all-MiniLM-L6-v2`, 384 dims, L2-normalized), and persisted to Supabase with a pgvector cosine index ready for retrieval. `GET /api/v1/documents` returns every ingested document with its chunk count.

The frontend still shows the Phase 1 Phaser canvas (controllable librarian sprite). The agent loop and real-time event stream come in Phase 3+.

See [docs/SESSION_LOG.md](docs/SESSION_LOG.md) for the full progress journal.

---

## What works today

| Feature | Status |
| --- | --- |
| `GET /healthz` liveness probe | ✅ |
| `POST /api/v1/documents` — multipart PDF → parse → chunk → embed → Supabase | ✅ |
| `GET /api/v1/documents` — list with `chunk_count` | ✅ |
| Supabase `documents` + `chunks` schema with `vector(384)` + ivfflat cosine index | ✅ |
| Phaser canvas with arrow-key-controllable librarian | ✅ |
| `POST /api/v1/query` — agentic answer via Librarian/Analyst/Auditor | ⏳ Phase 3 |
| `/ws/query/{job_id}` — live agent event stream | ⏳ Phase 4 |
| Sprite art + agent animations tied to events | ⏳ Phase 5 |

---

## Stack

| Layer        | Tech                                                                           |
| ------------ | ------------------------------------------------------------------------------ |
| Frontend     | React 19, Vite, TypeScript (strict), Phaser 4, Zustand, TanStack Query, Tailwind v4 |
| Backend      | FastAPI, LangGraph, Groq (Llama-3-70B inference — Phase 3)                     |
| Embeddings   | `sentence-transformers/all-MiniLM-L6-v2` — local, CPU, 384 dims, L2-normalized |
| Database     | Supabase (Postgres + pgvector, cosine ivfflat index)                           |
| Tooling      | pnpm workspaces, uv (Python), Node 22, Python 3.12                             |

Rationale for every major choice is in [docs/DECISIONS/](docs/DECISIONS/).

---

## Architecture at a glance

```
┌──────────────┐    REST     ┌──────────────┐    ┌─────────────┐
│ React +      │ ──────────▶ │   FastAPI    │ ─▶ │   Groq      │
│ Phaser UI    │ ◀ WebSocket │   (events)   │    │ Llama-3-70B │
└──────────────┘             │      │       │    └─────────────┘
                             │      ▼       │
                             │  LangGraph   │    ┌─────────────┐
                             │ Librarian →  │ ─▶ │  Supabase   │
                             │ Analyst →    │    │  pgvector   │
                             │ Auditor 🔁   │    └─────────────┘
                             └──────────────┘
```

The **Auditor** scores each draft in `[0, 1]`. A score below `0.8` routes the graph back to the Librarian with a refined query, up to `max_attempts = 3`. Low-confidence answers are surfaced to the UI rather than suppressed.

Full component + state diagrams: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Repository layout

```
cogniv-vault/
├── backend/                 FastAPI + LangGraph service (Python / uv)
│   ├── migrations/
│   │   └── 0001_init.sql    Supabase schema (apply via SQL editor)
│   ├── src/cogniv_vault/
│   │   ├── main.py          app factory, CORS, router mounts
│   │   ├── config.py        pydantic-settings
│   │   ├── api/             health, documents, query, ws, errors
│   │   ├── agents/          librarian, analyst, auditor, graph (Phase 3 stubs)
│   │   ├── ingestion/       pdf, chunking, embeddings
│   │   └── db/              supabase client
│   └── tests/               9 passing (chunking, embeddings, documents API, health)
├── frontend/                React + Phaser client (pnpm workspace)
│   └── src/
│       ├── api/client.ts       REST wrapper
│       ├── hooks/              WebSocket → Zustand bridge (stub)
│       ├── stores/agentStore   phase / score / answer
│       └── game/               Phaser scenes (BootScene, LibraryScene)
├── docs/
│   ├── ARCHITECTURE.md      component + agent-loop diagrams
│   ├── API_CONTRACTS.md     REST endpoints + WS event schema
│   ├── DATA_MODEL.md        Supabase schema + pgvector indexes
│   ├── SESSION_LOG.md       progress journal, resume notes
│   └── DECISIONS/           architecture decision records (ADRs)
└── .github/workflows/ci.yml frontend + backend pipelines
```

---

## Quickstart

### Prerequisites

- **Node 22** (use `nvm use` — repo has `.nvmrc`)
- **pnpm 10+** (`npm i -g pnpm`)
- **uv** (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Supabase project** (free tier is fine) — you'll need the Project URL and `service_role` key

### 1. Install

```bash
pnpm install        # frontend workspace
cd backend && uv sync && cd ..
```

### 2. Environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# fill in SUPABASE_URL + SUPABASE_SERVICE_KEY in backend/.env
# GROQ_API_KEY is only needed once Phase 3 lands
```

### 3. Apply the database schema (one-time per Supabase project)

Open your Supabase dashboard → SQL editor → paste the contents of [`backend/migrations/0001_init.sql`](backend/migrations/0001_init.sql) → run. Verify with:

```sql
select to_regclass('public.chunks');   -- should return 'chunks'
```

### 4. Run

Two terminals:

```bash
# terminal 1 — backend
cd backend && uv run uvicorn --app-dir src cogniv_vault.main:app --reload
```

```bash
# terminal 2 — frontend
pnpm --filter frontend dev
```

> **Note on `--app-dir src`.** hatchling's editable install writes a `.pth` file that `_virtualenv.pth` strips during site init, so `cogniv_vault` isn't importable via the plain uvicorn command. `--app-dir src` bypasses the broken editable path by adding `src/` directly. Accepted convention for now.

Open:

- API health → http://localhost:8000/healthz → `{"status":"ok"}`
- UI         → http://localhost:5173 → arrow keys move the librarian

### 5. Ingest a PDF

```bash
curl -F 'file=@path/to/your.pdf' http://localhost:8000/api/v1/documents
# → 202 {"document_id": "...", "filename": "your.pdf", "status": "queued"}

curl http://localhost:8000/api/v1/documents
# → {"documents": [{"id": "...", "filename": "your.pdf", "uploaded_at": "...", "chunk_count": 42}]}
```

First request will download the MiniLM model (~90 MB) into the HuggingFace cache. Subsequent requests are fast.

---

## Development

### Backend

```bash
cd backend
uv run pytest            # 9 tests, offline (no Supabase required)
uv run ruff check .      # lint
uv run mypy src          # strict type-check
```

### Frontend

```bash
pnpm --filter frontend lint
pnpm --filter frontend typecheck
pnpm --filter frontend build
pnpm --filter frontend format     # prettier
```

### Commit style

Conventional Commits (`feat:`, `fix:`, `docs:`, …). See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Roadmap

| Phase | Scope                                                                                  | Status |
| ----- | -------------------------------------------------------------------------------------- | ------ |
| 0     | Blueprint, ADRs, architecture docs                                                     | ✅     |
| 1     | Monorepo scaffold, FastAPI stub, Phaser canvas with controllable character             | ✅     |
| 2     | Supabase schema, PDF chunking, MiniLM embeddings, `POST /documents` end-to-end         | ✅     |
| 3     | LangGraph Librarian/Analyst/Auditor wired to Groq; retry-on-low-score enforced         | ⏳     |
| 4     | Real-time WebSocket event stream from agent nodes to UI                                | ⏳     |
| 5     | Sprite art, isometric library world, agent animations tied to phase events            | ⏳     |
| 6     | Vercel (frontend) + Render (backend) deploy, Supabase managed DB                       | ⏳     |

---

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API & WebSocket contracts](docs/API_CONTRACTS.md)
- [Data model](docs/DATA_MODEL.md)
- [Architecture Decision Records](docs/DECISIONS/)
- [Session log / resume notes](docs/SESSION_LOG.md)

---

## License

MIT — see [LICENSE](LICENSE). © 2026 Brandon Granillo.
