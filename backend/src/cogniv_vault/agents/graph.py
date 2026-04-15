"""LangGraph agent graph — Librarian -> Analyst -> Auditor with retry on score < threshold."""

from __future__ import annotations

from functools import lru_cache
from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from cogniv_vault.agents.analyst import analyst
from cogniv_vault.agents.auditor import auditor
from cogniv_vault.agents.librarian import librarian
from cogniv_vault.config import get_settings


class Hit(TypedDict):
    chunk_id: str
    document_id: str
    ordinal: int
    content: str
    similarity: float


class AgentState(TypedDict, total=False):
    question: str
    refined_query: str
    document_ids: list[str] | None
    hits: list[Hit]
    draft: str
    score: float
    critique: str
    attempt: int
    max_attempts: int
    threshold: float
    answer: str
    low_confidence: bool
    citations: list[Hit]
    started_at: float


async def finalize(state: AgentState) -> AgentState:
    score = float(state.get("score", 0.0))
    threshold = float(state.get("threshold", get_settings().verify_threshold))
    return {
        **state,
        "answer": state.get("draft", ""),
        "low_confidence": score < threshold,
        "citations": list(state.get("hits", [])),
    }


def _route_after_auditor(state: AgentState) -> str:
    score = float(state.get("score", 0.0))
    threshold = float(state.get("threshold", get_settings().verify_threshold))
    attempt = int(state.get("attempt", 1))
    max_attempts = int(state.get("max_attempts", get_settings().max_attempts))

    if score >= threshold or attempt >= max_attempts:
        return "finalize"
    return "retry"


async def _bump_attempt(state: AgentState) -> AgentState:
    return {**state, "attempt": int(state.get("attempt", 1)) + 1}


@lru_cache(maxsize=1)
def build_graph() -> Any:
    graph: StateGraph[AgentState] = StateGraph(AgentState)
    graph.add_node("librarian", librarian)
    graph.add_node("analyst", analyst)
    graph.add_node("auditor", auditor)
    graph.add_node("finalize", finalize)
    graph.add_node("bump_attempt", _bump_attempt)

    graph.add_edge(START, "librarian")
    graph.add_edge("librarian", "analyst")
    graph.add_edge("analyst", "auditor")
    graph.add_conditional_edges(
        "auditor",
        _route_after_auditor,
        {"finalize": "finalize", "retry": "bump_attempt"},
    )
    graph.add_edge("bump_attempt", "librarian")
    graph.add_edge("finalize", END)

    return graph.compile()
