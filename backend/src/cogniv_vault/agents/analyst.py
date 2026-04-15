"""Analyst — drafts a grounded answer from retrieved chunks via Groq."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from cogniv_vault.agents.prompts import build_analyst_messages
from cogniv_vault.llm.groq_client import chat

if TYPE_CHECKING:
    from cogniv_vault.agents.graph import AgentState


async def analyst(state: AgentState) -> AgentState:
    question = state["question"]
    hits = state.get("hits", [])
    messages = build_analyst_messages(question, cast("list[dict[str, object]]", hits))
    draft = await chat(messages, temperature=0.2)
    return {**state, "draft": draft.strip()}
