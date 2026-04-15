"""End-to-end graph tests. All Groq + Supabase calls are mocked."""

from __future__ import annotations

import json

import pytest

from cogniv_vault.agents.graph import build_graph
from cogniv_vault.agents.runner import run_graph
from tests.conftest import FakeSupabaseRpc, ScriptedGroq


@pytest.fixture(autouse=True)
def _clear_graph_cache() -> None:
    build_graph.cache_clear()


@pytest.mark.asyncio
async def test_single_pass_success(
    fake_groq: ScriptedGroq, fake_supabase_rpc: FakeSupabaseRpc
) -> None:
    fake_groq.push([
        "Mitochondria produce ATP [1][2].",
        json.dumps({"score": 0.92, "critique": "well-grounded", "refined_query": None}),
    ])

    result = await run_graph("what makes ATP?")

    assert result["low_confidence"] is False
    assert result["trace"]["attempts"] == 1
    assert result["answer"].startswith("Mitochondria")
    assert result["confidence"] == pytest.approx(0.92)
    assert len(result["citations"]) == 2
    assert result["citations"][0]["snippet"].startswith("The mitochondrion")


@pytest.mark.asyncio
async def test_retry_path_success_on_second(
    fake_groq: ScriptedGroq, fake_supabase_rpc: FakeSupabaseRpc
) -> None:
    fake_groq.push([
        "weak first draft",
        json.dumps({"score": 0.5, "critique": "unsupported", "refined_query": "ATP synthesis location"}),
        "Mitochondria synthesize ATP via oxidative phosphorylation [1].",
        json.dumps({"score": 0.85, "critique": "supported", "refined_query": None}),
    ])

    result = await run_graph("where is ATP made?")

    assert result["trace"]["attempts"] == 2
    assert result["low_confidence"] is False
    assert result["confidence"] == pytest.approx(0.85)


@pytest.mark.asyncio
async def test_hard_fail_after_max_attempts(
    fake_groq: ScriptedGroq, fake_supabase_rpc: FakeSupabaseRpc
) -> None:
    fake_groq.push([
        "draft 1",
        json.dumps({"score": 0.3, "critique": "off-topic", "refined_query": "q2"}),
        "draft 2",
        json.dumps({"score": 0.3, "critique": "still off", "refined_query": "q3"}),
        "draft 3",
        json.dumps({"score": 0.3, "critique": "no support", "refined_query": None}),
    ])

    result = await run_graph("unanswerable question")

    assert result["trace"]["attempts"] == 3
    assert result["low_confidence"] is True
    assert result["answer"] == "draft 3"
    assert result["confidence"] == pytest.approx(0.3)
