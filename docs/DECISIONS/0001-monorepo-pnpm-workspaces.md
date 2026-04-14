# ADR 0001 — Monorepo with pnpm workspaces

**Status:** Accepted
**Date:** 2026-04-13

## Context

Cogniv-Vault has two runtime targets — a Python FastAPI backend and a React/Phaser frontend — plus shared documentation. We need a single repository that supports independent tooling per target while keeping cross-cutting changes (API contract updates, ADRs, CI) atomic.

## Decision

Use a single Git repository organized as a pnpm workspace.

- `frontend/` is the only pnpm workspace package.
- `backend/` is a Python project managed by `uv` — it is *not* a pnpm package, and `pnpm-workspace.yaml` does not reference it.
- Root `package.json` holds meta scripts (`dev`, `build`, `lint`, `typecheck`) that delegate via `pnpm --filter` or `pnpm -r`.

## Alternatives considered

- **Turborepo / Nx** — richer caching and task graphs, but overkill for two packages. Can be layered on top of pnpm workspaces later without a migration.
- **Two separate repos** — rejected: API contract changes would require coordinated PRs, and ADRs/docs would have no natural home.
- **npm / yarn workspaces** — pnpm is faster, uses less disk, and has stricter dependency isolation by default.

## Consequences

- One `pnpm install` at root bootstraps the frontend.
- CI can run frontend and backend jobs in parallel with distinct setup steps.
- If a third JS package is ever added, it joins `pnpm-workspace.yaml` with zero ceremony.
