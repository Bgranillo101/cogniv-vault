# Cogniv-Vault Frontend

React + Vite + TypeScript + Phaser.js client. Phase 1 demo: arrow-key controllable pixel character on a Phaser canvas.

## Prerequisites

- Node 22+
- pnpm 10+

## Setup

```bash
cp .env.example .env
pnpm install     # run from repo root
```

## Run

```bash
pnpm --filter frontend dev
```

Open http://localhost:5173.

## Scripts

- `pnpm --filter frontend dev` — Vite dev server
- `pnpm --filter frontend build` — production build
- `pnpm --filter frontend lint` — ESLint
- `pnpm --filter frontend typecheck` — TypeScript strict check
- `pnpm --filter frontend format` — Prettier

## Layout

```
src/
├── App.tsx
├── main.tsx
├── index.css
├── api/client.ts              # REST wrapper for FastAPI
├── hooks/useAgentSocket.ts    # WS stream -> Zustand
├── stores/agentStore.ts       # agent phase/score/answer
└── game/
    ├── PhaserGame.tsx         # React ↔ Phaser bridge
    └── scenes/
        ├── BootScene.ts       # placeholder sprite generation
        └── LibraryScene.ts    # arrow-key controllable character
```
