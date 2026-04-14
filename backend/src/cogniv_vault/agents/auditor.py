"""Auditor — scores the draft for grounding/accuracy. Retry if score < threshold. Phase 3 stub."""

from cogniv_vault.agents.graph import AgentState


async def auditor(state: AgentState) -> AgentState:
    raise NotImplementedError("auditor verification is Phase 3")
