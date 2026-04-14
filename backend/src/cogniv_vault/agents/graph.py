"""LangGraph agent graph — Librarian -> Analyst -> Auditor with retry on score < threshold.

Phase 1: stub. Real graph wiring is deferred to Phase 3.
"""

from typing import TypedDict


class AgentState(TypedDict, total=False):
    question: str
    document_ids: list[str] | None
    context: list[dict[str, str]]
    draft: str
    score: float
    critique: str
    attempt: int
    answer: str
    low_confidence: bool


def build_graph() -> object:
    raise NotImplementedError("agent graph wiring is Phase 3")
