# Cogniv-Vault

> An **observable agentic RAG system** — a Librarian → Analyst → Auditor agent loop that ingests documents, answers queries, and streams its internal state to a **Phaser.js pixel-art visualization** in real time.

Most RAG systems are black boxes: you submit a question, wait, and receive an answer. Cogniv-Vault treats the agent pipeline as a first-class observability surface — every retrieval, draft, and verification step becomes an event that the UI renders as animated agents working inside a tiny library. You don't just see the answer; you see *how the machine got there.*

---

## Status

**Phase 1 scaffold complete.** You can run the backend, hit `/healthz`, launch the frontend, and drive a pixel-art librarian around a Phaser canvas with arrow keys. Ingestion, embeddings, and the real LangGraph loop land in Phase 2+.

See [docs/SESSION_LOG.md](docs/SESSION_LOG.md) for what exists today and what's next.

---

## Stack

| Layer        | Tech                                                                 |
| ------------ | -------------------------------------------------------------------- |
| Frontend     | React 19, Vite, TypeScript (strict), Phaser 4, Zustand, TanStack Query, Tailwind v4 |
| Backend      | FastAPI, LangGraph, Groq (Llama-3-70B inference)                     |
| Embeddings   | `sentence-transformers/all-MiniLM-L6-v2` — local, CPU, 384 dims      |
| Database     | Supabase (Postgres + pgvector, cosine ivfflat index)                 |
| Tooling      | pnpm workspaces, uv (Python), Node 22, Python 3.12                   |

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
│   ├── src/cogniv_vault/
│   │   ├── main.py          app factory, CORS, router mounts
│   │   ├── config.py        pydantic-settings
│   │   ├── api/             health, documents, query, ws
│   │   ├── agents/          librarian, analyst, auditor, graph
│   │   ├── ingestion/       chunking, embeddings
│   │   └── db/              supabase client
│   └── tests/
├── frontend/                React + Phaser client (pnpm workspace)
│   └── src/
│       ├── api/client.ts       REST wrapper
│       ├── hooks/              WebSocket → Zustand bridge
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

### 1. Install

```bash
pnpm install        # frontend workspace
cd backend && uv sync && cd ..
```

### 2. Environment

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# fill in GROQ_API_KEY, SUPABASE_URL, SUPABASE_SERVICE_KEY when you reach Phase 2
```

### 3. Run

Two terminals:

```bash
# terminal 1 — backend
cd backend && uv run uvicorn cogniv_vault.main:app --reload
```

```bash
# terminal 2 — frontend
pnpm --filter frontend dev
```

Open:

- API health → http://localhost:8000/healthz → `{"status":"ok"}`
- UI         → http://localhost:5173 → arrow keys move the librarian

---

## Development

### Backend

```bash
cd backend
uv run pytest            # tests
uv run ruff check .      # lint
uv run mypy src          # type-check
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
| 2     | Supabase schema, PDF chunking, MiniLM embeddings, `POST /documents` end-to-end         | ⏳     |
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
