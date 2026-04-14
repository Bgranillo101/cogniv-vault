"""Documents API — PDF upload + list."""

from __future__ import annotations

import asyncio
from typing import Any

from fastapi import APIRouter, UploadFile
from fastapi.responses import JSONResponse

from cogniv_vault.api.errors import error_response
from cogniv_vault.db.client import get_supabase_client
from cogniv_vault.ingestion.chunking import chunk_text
from cogniv_vault.ingestion.embeddings import embed
from cogniv_vault.ingestion.pdf import extract_text

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_BYTES = 25 * 1024 * 1024
EMBED_BATCH = 32


def _insert_chunks_batched(
    supabase: Any, document_id: str, contents: list[str], token_counts: list[int]
) -> None:
    for start in range(0, len(contents), EMBED_BATCH):
        batch_texts = contents[start : start + EMBED_BATCH]
        batch_tokens = token_counts[start : start + EMBED_BATCH]
        vectors = embed(batch_texts)
        rows = [
            {
                "document_id": document_id,
                "ordinal": start + i,
                "content": batch_texts[i],
                "token_count": batch_tokens[i],
                "embedding": vectors[i],
            }
            for i in range(len(batch_texts))
        ]
        supabase.table("chunks").insert(rows).execute()


def _ingest_sync(file_bytes: bytes, filename: str) -> dict[str, Any]:
    supabase = get_supabase_client()
    full_text, page_count = extract_text(file_bytes)

    doc_row = (
        supabase.table("documents")
        .insert(
            {
                "filename": filename,
                "byte_size": len(file_bytes),
                "page_count": page_count,
                "status": "processing",
            }
        )
        .execute()
    )
    inserted_rows: list[dict[str, Any]] = doc_row.data  # type: ignore[assignment]
    document_id: str = str(inserted_rows[0]["id"])

    try:
        chunks = chunk_text(full_text)
        if chunks:
            _insert_chunks_batched(
                supabase,
                document_id,
                [c["content"] for c in chunks],
                [c["token_count"] for c in chunks],
            )
        supabase.table("documents").update({"status": "ready"}).eq(
            "id", document_id
        ).execute()
    except Exception:
        supabase.table("documents").update({"status": "failed"}).eq(
            "id", document_id
        ).execute()
        raise

    return {"document_id": document_id, "filename": filename, "status": "queued"}


@router.post("", status_code=202)
async def upload_document(file: UploadFile) -> JSONResponse:
    if file.content_type != "application/pdf":
        return error_response(
            "unsupported_media_type",
            "expected application/pdf",
            detail={"content_type": file.content_type},
            status=415,
        )
    data = await file.read()
    if len(data) == 0:
        return error_response("empty_file", "uploaded file is empty", status=400)
    if len(data) > MAX_BYTES:
        return error_response(
            "payload_too_large",
            "file exceeds 25 MB limit",
            detail={"byte_size": len(data), "limit": MAX_BYTES},
            status=413,
        )

    filename = file.filename or "upload.pdf"
    try:
        result = await asyncio.to_thread(_ingest_sync, data, filename)
    except ValueError as exc:
        return error_response("invalid_pdf", str(exc), status=400)
    except Exception as exc:
        return error_response(
            "ingestion_failed",
            "ingestion failed",
            detail={"reason": str(exc)},
            status=500,
        )
    return JSONResponse(status_code=202, content=result)


def _list_sync() -> list[dict[str, Any]]:
    supabase = get_supabase_client()
    resp = (
        supabase.table("documents")
        .select("id, filename, uploaded_at, chunks(count)")
        .order("uploaded_at", desc=True)
        .execute()
    )
    rows: list[dict[str, Any]] = resp.data or []  # type: ignore[assignment]
    out: list[dict[str, Any]] = []
    for row in rows:
        chunk_rel = row.get("chunks") or []
        chunk_count = chunk_rel[0]["count"] if chunk_rel else 0
        out.append(
            {
                "id": row["id"],
                "filename": row["filename"],
                "uploaded_at": row["uploaded_at"],
                "chunk_count": chunk_count,
            }
        )
    return out


@router.get("")
async def list_documents() -> dict[str, list[dict[str, Any]]]:
    docs = await asyncio.to_thread(_list_sync)
    return {"documents": docs}
