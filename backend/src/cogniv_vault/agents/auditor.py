"""Auditor — JSON-mode scoring of the draft against retrieved chunks."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from cogniv_vault.agents.prompts import build_auditor_messages
from cogniv_vault.llm.groq_client import chat

if TYPE_CHECKING:
    from cogniv_vault.agents.graph import AgentState


async def auditor(state: AgentState) -> AgentState:
    question = state["question"]
    hits = state.get("hits", [])
    draft = state.get("draft", "")

    messages = build_auditor_messages(
        question, cast("list[dict[str, object]]", hits), draft
    )
    raw = await chat(
        messages,
        temperature=0.0,
        response_format={"type": "json_object"},
    )

    try:
        parsed: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"score": 0.0, "critique": "auditor returned non-JSON", "refined_query": None}

    score = max(0.0, min(1.0, float(parsed.get("score", 0.0))))
    critique = str(parsed.get("critique", ""))
    refined = parsed.get("refined_query")

    out: AgentState = {**state, "score": score, "critique": critique}
    if isinstance(refined, str) and refined.strip():
        out["refined_query"] = refined.strip()
    return out
