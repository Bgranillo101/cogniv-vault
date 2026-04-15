"""Invoke the compiled agent graph and shape the terminal AGENT_RESULT payload."""

from __future__ import annotations

import time
from typing import Any

from cogniv_vault.agents.graph import AgentState, build_graph
from cogniv_vault.config import get_settings


async def run_graph(
    question: str,
    document_ids: list[str] | None = None,
) -> dict[str, Any]:
    settings = get_settings()
    initial: AgentState = {
        "question": question,
        "document_ids": document_ids,
        "attempt": 1,
        "max_attempts": settings.max_attempts,
        "threshold": settings.verify_threshold,
        "started_at": time.perf_counter(),
    }

    graph = build_graph()
    final: AgentState = await graph.ainvoke(initial)

    duration_ms = int((time.perf_counter() - float(final.get("started_at", time.perf_counter()))) * 1000)
    citations = [
        {
            "chunk_id": c["chunk_id"],
            "document_id": c["document_id"],
            "snippet": c["content"][:200],
        }
        for c in final.get("citations", [])
    ]

    return {
        "answer": final.get("answer", ""),
        "confidence": float(final.get("score", 0.0)),
        "low_confidence": bool(final.get("low_confidence", False)),
        "citations": citations,
        "trace": {
            "attempts": int(final.get("attempt", 1)),
            "final_score": float(final.get("score", 0.0)),
            "duration_ms": duration_ms,
        },
    }
