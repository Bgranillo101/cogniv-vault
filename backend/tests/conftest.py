"""Shared test fixtures — scripted Groq + Supabase doubles for Phase 3 tests."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pytest


class ScriptedGroq:
    """Queue of canned Groq responses, consumed in order."""

    def __init__(self) -> None:
        self._queue: list[str] = []

    def push(self, responses: Iterable[str]) -> None:
        self._queue.extend(responses)

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        response_format: dict[str, str] | None = None,
    ) -> str:
        if not self._queue:
            raise AssertionError("ScriptedGroq queue exhausted — script more responses")
        return self._queue.pop(0)


@pytest.fixture
def fake_groq(monkeypatch: pytest.MonkeyPatch) -> ScriptedGroq:
    scripted = ScriptedGroq()
    # Patch the three import sites (analyst, auditor, and the module itself).
    from cogniv_vault.agents import analyst as analyst_mod
    from cogniv_vault.agents import auditor as auditor_mod
    from cogniv_vault.llm import groq_client

    monkeypatch.setattr(groq_client, "chat", scripted.chat)
    monkeypatch.setattr(analyst_mod, "chat", scripted.chat)
    monkeypatch.setattr(auditor_mod, "chat", scripted.chat)
    return scripted


class FakeRpcResult:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class FakeRpcQuery:
    def __init__(self, data: list[dict[str, Any]]):
        self._data = data

    def execute(self) -> FakeRpcResult:
        return FakeRpcResult(self._data)


class FakeSupabaseRpc:
    def __init__(self, hits: list[dict[str, Any]]) -> None:
        self.hits = hits
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def rpc(self, name: str, params: dict[str, Any]) -> FakeRpcQuery:
        self.calls.append((name, params))
        return FakeRpcQuery(self.hits)


@pytest.fixture
def fake_supabase_rpc(monkeypatch: pytest.MonkeyPatch) -> FakeSupabaseRpc:
    hits = [
        {
            "chunk_id": "11111111-1111-1111-1111-111111111111",
            "document_id": "22222222-2222-2222-2222-222222222222",
            "ordinal": 0,
            "content": "The mitochondrion is the powerhouse of the cell.",
            "similarity": 0.91,
        },
        {
            "chunk_id": "33333333-3333-3333-3333-333333333333",
            "document_id": "22222222-2222-2222-2222-222222222222",
            "ordinal": 1,
            "content": "ATP is produced during cellular respiration.",
            "similarity": 0.88,
        },
    ]
    fake = FakeSupabaseRpc(hits)
    from cogniv_vault.agents import librarian as librarian_mod

    monkeypatch.setattr(librarian_mod, "get_supabase_client", lambda: fake)
    monkeypatch.setattr(librarian_mod, "embed", lambda texts: [[0.0] * 384 for _ in texts])
    return fake
