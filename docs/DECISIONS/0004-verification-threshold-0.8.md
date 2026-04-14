# ADR 0004 — Auditor verification threshold: 0.8

**Status:** Accepted
**Date:** 2026-04-13

## Context

The Auditor agent scores each draft answer for grounding and accuracy on a `[0, 1]` scale and must decide: accept, retry, or return with low-confidence flag. The threshold is a product/engineering decision, not a statistical derivation — the score is an LLM self-assessment and is inherently noisy.

## Decision

- **Pass threshold:** `score >= 0.8` → return `AGENT_RESULT` to the client.
- **Retry:** `score < 0.8` AND `attempt < max_attempts` → re-enter Librarian with a refined query.
- **Max attempts:** `3` total (initial + 2 retries).
- **Exhaustion:** return the last draft with `low_confidence: true`; do not hide the answer.

## Rationale

- `0.8` sits above typical LLM self-grading noise (~0.6–0.7 for weak answers) while remaining achievable on well-grounded responses.
- Capping retries bounds tail latency (each retry ≈ one full graph traversal) and Groq token spend.
- Returning low-confidence answers (rather than errors) preserves UX — the UI can render the caveat.

## Alternatives considered

- **0.7 threshold** — too permissive; hallucinated answers frequently self-score above this.
- **0.9 threshold** — too strict; forces retries on adequate answers, inflates latency and cost.
- **Unbounded retries** — unbounded latency; rejected.
- **Hard-fail on low score** — worse UX; the user can often judge a flagged answer themselves.

## Consequences

- Threshold, max attempts, and low-confidence behavior must be configurable (env vars: `VERIFY_THRESHOLD`, `MAX_ATTEMPTS`).
- Once we have real eval data, revisit — this ADR should be superseded with a data-driven threshold.
