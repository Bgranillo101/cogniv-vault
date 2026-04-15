# ADR 0005 — Groq model choice and JSON-mode for the Auditor

**Status:** Accepted — 2026-04-14
**Context:** Phase 3 (agent loop)

## Decision

- The Analyst and Auditor both call Groq with `model = llama-3.3-70b-versatile` (configurable via `GROQ_MODEL`).
- The Auditor invokes with `response_format={"type": "json_object"}` and `temperature=0.0`.
- The Analyst uses `temperature=0.2` for slight draft variability.

## Why `llama-3.3-70b-versatile`

- 128k context window comfortably holds 5 × 220-token chunks plus prompt scaffolding with room to spare.
- Groq's hosted 70B inference is fast enough (~300 tok/s) that a two- or three-pass agent loop still returns in single-digit seconds.
- Production-ready on Groq's catalog (not a preview/beta endpoint that can disappear mid-development).
- Strong instruction-following and JSON adherence — important for the Auditor's scoring contract.

Alternatives weighed:

- **llama-3.1-8b-instant** — faster, but worse at the nuanced "score how well this draft is grounded in these excerpts" task; pilot runs gave noisier scores.
- **mixtral-8x7b** — deprecated on Groq.
- **OpenAI gpt-4o-mini** — capable, but adds a second vendor dependency and latency is meaningfully worse than Groq for the same quality tier.

## Why JSON-mode for the Auditor

The Auditor's output feeds directly into the graph's conditional routing (`score >= threshold → finalize, else retry`). We need a parseable contract, not free-form prose:

```json
{ "score": 0.0..1.0, "critique": "…", "refined_query": "…" | null }
```

Groq's `response_format={"type": "json_object"}` constrains the model to emit syntactically valid JSON. Combined with `temperature=0.0`, this eliminates the "strip the code fence, hope for the best" failure mode that plagued earlier prototypes.

The parser still clamps `score` into `[0.0, 1.0]` and tolerates a missing `refined_query` — defense in depth.

## Consequences

- The model name is pinned; changing it is one config/env change, but re-validation of Auditor scoring behavior is required before promoting a new model.
- If Groq deprecates or renames the endpoint, the agent loop goes down until `GROQ_MODEL` is updated. Tracked as operational risk; revisit if the model moves to legacy status.
