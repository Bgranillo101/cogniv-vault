"""POST /query + GET /query/{job_id} — round-trip with mocked agent graph."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from cogniv_vault.api import query as query_mod
from cogniv_vault.main import app


@pytest.fixture
def fake_run_graph(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "answer": "mocked answer",
        "confidence": 0.9,
        "low_confidence": False,
        "citations": [
            {"chunk_id": "c1", "document_id": "d1", "snippet": "snippet text"}
        ],
        "trace": {"attempts": 1, "final_score": 0.9, "duration_ms": 7},
    }

    async def _fake(question: str, document_ids: list[str] | None = None) -> dict[str, Any]:
        return payload

    monkeypatch.setattr(query_mod, "run_graph", _fake)
    return payload


@pytest.mark.asyncio
async def test_post_then_get_returns_result(fake_run_graph: dict[str, Any]) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        post = await client.post("/api/v1/query", json={"question": "hi"})
        assert post.status_code == 202, post.text
        job_id = post.json()["job_id"]
        assert job_id

        get = await client.get(f"/api/v1/query/{job_id}")
        assert get.status_code == 200
        assert get.json() == fake_run_graph

        # One-shot eviction: second GET is 404.
        again = await client.get(f"/api/v1/query/{job_id}")
        assert again.status_code == 404
        assert again.json()["error"]["code"] == "not_found"


@pytest.mark.asyncio
async def test_post_rejects_empty_question(fake_run_graph: dict[str, Any]) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/query", json={"question": "   "})
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "invalid_request"
