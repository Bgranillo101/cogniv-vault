# ADR 0003 — Embedding model: all-MiniLM-L6-v2

**Status:** Accepted
**Date:** 2026-04-13

## Context

The project uses Groq for LLM inference. Groq does **not** expose an embeddings API, so embeddings must be produced by another path. Constraints: free tier preferred, CPU-capable (no GPU budget in Phase 1), reasonable retrieval quality on English technical text.

## Decision

Use `sentence-transformers/all-MiniLM-L6-v2` running locally via the `sentence-transformers` Python library.

- **Dimensions:** 384 → Postgres column type `vector(384)`.
- **Distance metric:** cosine (pgvector `<=>`).
- **Runtime:** CPU; ~5–20ms per chunk on modern laptops.
- **License:** Apache 2.0.

## Alternatives considered

- **OpenAI `text-embedding-3-small` (1536 dim)** — strong quality but paid, and adds a second vendor dependency. Rejected for Phase 1; reconsider if retrieval quality is insufficient.
- **Cohere embed-v3** — paid, similar tradeoffs.
- **`bge-small-en-v1.5` (384 dim)** — competitive quality, same dim, also viable. MiniLM chosen for smaller model size and mature tooling; can A/B later without schema change.
- **Instructor XL / large models** — higher quality but slow on CPU and much larger memory footprint.

## Consequences

- Zero marginal cost for embeddings.
- Swapping models later requires re-embedding (schema is dim-locked); a future ADR will cover that migration if/when it happens.
- First model download (~90 MB) is cached under `~/.cache/huggingface/` on first run; CI should cache this path.
