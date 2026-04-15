"""Librarian — embeds the (refined) query and retrieves top-k chunks via pgvector RPC."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, cast

from cogniv_vault.config import get_settings
from cogniv_vault.db.client import get_supabase_client
from cogniv_vault.ingestion.embeddings import embed

if TYPE_CHECKING:
    from cogniv_vault.agents.graph import AgentState, Hit


async def librarian(state: AgentState) -> AgentState:
    query = state.get("refined_query") or state["question"]
    document_ids = state.get("document_ids")
    top_k = get_settings().top_k

    def _run() -> list[dict[str, Any]]:
        vector = embed([query])[0]
        client = get_supabase_client()
        params: dict[str, Any] = {
            "query_embedding": vector,
            "match_count": top_k,
            "document_ids": document_ids,
        }
        resp = client.rpc("match_chunks", params).execute()
        rows: list[dict[str, Any]] = resp.data or []  # type: ignore[assignment]
        return rows

    rows = await asyncio.to_thread(_run)
    hits: list[Hit] = [
        cast(
            "Hit",
            {
                "chunk_id": str(r["chunk_id"]),
                "document_id": str(r["document_id"]),
                "ordinal": int(r["ordinal"]),
                "content": str(r["content"]),
                "similarity": float(r["similarity"]),
            },
        )
        for r in rows
    ]
    return {**state, "hits": hits}
