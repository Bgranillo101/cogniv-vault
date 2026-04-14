# ADR 0002 — Python tooling: uv

**Status:** Accepted
**Date:** 2026-04-13

## Context

The backend needs a dependency manager, virtualenv manager, and lockfile. The Python ecosystem has several competing options (pip + venv, Poetry, PDM, Rye, uv).

## Decision

Use [`uv`](https://docs.astral.sh/uv/) (Astral) for dependency resolution, virtualenv management, and locking.

- `pyproject.toml` is the source of truth for deps.
- `uv.lock` is committed.
- `uv run <cmd>` executes inside the managed venv without manual activation.
- `.python-version` pins Python 3.12; `uv` auto-downloads if missing.

## Alternatives considered

- **Poetry** — mature but slow resolver; lockfile format churn historically.
- **PDM** — capable, but smaller ecosystem than Poetry/uv.
- **pip + venv + pip-tools** — works, but three tools to learn and coordinate.
- **Rye** — Astral acquired it and is consolidating into uv; starting with uv avoids a future migration.

## Consequences

- Resolution and installs are ~10–100× faster than Poetry in practice.
- Single binary, single lockfile, single config.
- Contributors need `uv` installed (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`).
- CI uses `astral-sh/setup-uv` action for a one-line install.
