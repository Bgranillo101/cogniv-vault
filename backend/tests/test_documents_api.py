from __future__ import annotations

import uuid
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from cogniv_vault.api import documents as documents_mod
from cogniv_vault.main import app


class FakeResult:
    def __init__(self, data: list[dict[str, Any]]):
        self.data = data


class FakeQuery:
    def __init__(self, table: FakeTable, op: str, payload: Any = None):
        self._table = table
        self._op = op
        self._payload = payload
        self._eq: tuple[str, Any] | None = None

    def eq(self, col: str, val: Any) -> FakeQuery:
        self._eq = (col, val)
        return self

    def order(self, *_: Any, **__: Any) -> FakeQuery:
        return self

    def execute(self) -> FakeResult:
        if self._op == "insert":
            rows = self._payload if isinstance(self._payload, list) else [self._payload]
            inserted = []
            for row in rows:
                record = dict(row)
                record.setdefault("id", str(uuid.uuid4()))
                self._table.rows.append(record)
                inserted.append(record)
            return FakeResult(inserted)
        if self._op == "update":
            assert self._eq is not None
            col, val = self._eq
            for row in self._table.rows:
                if row.get(col) == val:
                    row.update(self._payload)
            return FakeResult([])
        if self._op == "select":
            return FakeResult(list(self._table.rows))
        raise AssertionError(f"unexpected op {self._op}")


class FakeTable:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def insert(self, payload: Any) -> FakeQuery:
        return FakeQuery(self, "insert", payload)

    def update(self, payload: dict[str, Any]) -> FakeQuery:
        return FakeQuery(self, "update", payload)

    def select(self, *_: Any, **__: Any) -> FakeQuery:
        return FakeQuery(self, "select")


class FakeSupabase:
    def __init__(self) -> None:
        self.tables: dict[str, FakeTable] = {
            "documents": FakeTable(),
            "chunks": FakeTable(),
        }

    def table(self, name: str) -> FakeTable:
        return self.tables[name]


@pytest.fixture
def fake_supabase(monkeypatch: pytest.MonkeyPatch) -> FakeSupabase:
    fake = FakeSupabase()
    monkeypatch.setattr(documents_mod, "get_supabase_client", lambda: fake)
    monkeypatch.setattr(
        documents_mod,
        "extract_text",
        lambda _b: ("some extracted text content for ingestion tests", 1),
    )
    monkeypatch.setattr(
        documents_mod,
        "chunk_text",
        lambda _t, **__: [
            {"ordinal": 0, "content": "chunk a", "token_count": 3},
            {"ordinal": 1, "content": "chunk b", "token_count": 3},
        ],
    )
    monkeypatch.setattr(
        documents_mod, "embed", lambda texts: [[0.0] * 384 for _ in texts]
    )
    return fake


@pytest.mark.asyncio
async def test_upload_pdf_happy_path(fake_supabase: FakeSupabase) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/documents",
            files={"file": ("sample.pdf", b"%PDF-1.4\n%fake\n", "application/pdf")},
        )

    assert resp.status_code == 202, resp.text
    body = resp.json()
    assert body["filename"] == "sample.pdf"
    assert body["status"] == "queued"
    assert "document_id" in body

    docs = fake_supabase.tables["documents"].rows
    assert len(docs) == 1
    assert docs[0]["status"] == "ready"

    chunks = fake_supabase.tables["chunks"].rows
    assert len(chunks) == 2
    for c in chunks:
        assert len(c["embedding"]) == 384
        assert c["document_id"] == docs[0]["id"]


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf(fake_supabase: FakeSupabase) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/documents",
            files={"file": ("x.txt", b"hello", "text/plain")},
        )
    assert resp.status_code == 415
    assert resp.json()["error"]["code"] == "unsupported_media_type"
