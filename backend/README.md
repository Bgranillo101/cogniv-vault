# Cogniv-Vault Backend

FastAPI + LangGraph service hosting the Librarian → Analyst → Auditor agent loop.

## Prerequisites

- Python 3.12 (managed automatically by `uv`)
- [`uv`](https://docs.astral.sh/uv/) installed

## Setup

```bash
cp .env.example .env
uv sync
```

## Run

```bash
uv run uvicorn cogniv_vault.main:app --reload
```

Open http://localhost:8000/healthz.

## Test

```bash
uv run pytest
```

## Lint & type-check

```bash
uv run ruff check .
uv run mypy src
```

## Layout

```
src/cogniv_vault/
├── main.py              # FastAPI app factory
├── config.py            # Settings (pydantic-settings)
├── api/                 # HTTP + WS routers
│   ├── health.py
│   ├── documents.py
│   ├── query.py
│   └── ws.py
├── agents/              # LangGraph nodes (stubs in Phase 1)
│   ├── graph.py
│   ├── librarian.py
│   ├── analyst.py
│   └── auditor.py
├── ingestion/           # PDF chunking + embeddings (stubs in Phase 1)
│   ├── chunking.py
│   └── embeddings.py
└── db/
    └── client.py        # Supabase client factory
```
