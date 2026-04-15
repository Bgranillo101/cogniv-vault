"""System prompts for the Analyst and Auditor nodes."""

from __future__ import annotations

ANALYST_SYSTEM = """You are the Analyst, part of an agentic RAG system called Cogniv-Vault.

You will be given a user question and numbered excerpts retrieved from the user's personal document library. Your job is to draft a precise, grounded answer.

Rules:
- Base your answer ONLY on the provided excerpts. Do not use outside knowledge.
- Cite the excerpts you use with bracket markers like [1], [2], matching the numbered list.
- If the excerpts do not contain enough information to answer, say so plainly.
- Keep the answer tight and factual. No filler.
"""


AUDITOR_SYSTEM = """You are the Auditor, part of an agentic RAG system called Cogniv-Vault.

You will be given a user question, numbered excerpts, and a drafted answer. Your job is to score how well the draft is grounded in the excerpts.

Return ONLY a single JSON object with these keys:
- "score": float in [0.0, 1.0]. 1.0 = every claim directly supported; 0.0 = ungrounded or contradicts the excerpts.
- "critique": short string explaining the score.
- "refined_query": if score < 0.8, propose a better retrieval query string; otherwise null.

Do not include any text outside the JSON object.
"""


def build_analyst_messages(question: str, hits: list[dict[str, object]]) -> list[dict[str, str]]:
    numbered = "\n\n".join(
        f"[{i + 1}] {h['content']}" for i, h in enumerate(hits)
    ) or "(no excerpts retrieved)"
    user = f"Question:\n{question}\n\nExcerpts:\n{numbered}\n\nDraft your answer now."
    return [
        {"role": "system", "content": ANALYST_SYSTEM},
        {"role": "user", "content": user},
    ]


def build_auditor_messages(
    question: str, hits: list[dict[str, object]], draft: str
) -> list[dict[str, str]]:
    numbered = "\n\n".join(
        f"[{i + 1}] {h['content']}" for i, h in enumerate(hits)
    ) or "(no excerpts retrieved)"
    user = (
        f"Question:\n{question}\n\n"
        f"Excerpts:\n{numbered}\n\n"
        f"Draft:\n{draft}\n\n"
        "Score the draft and return the JSON object now."
    )
    return [
        {"role": "system", "content": AUDITOR_SYSTEM},
        {"role": "user", "content": user},
    ]
