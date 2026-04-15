"""Query API — POST submits, GET retrieves. Phase 3: synchronous run, poll for result."""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from cogniv_vault.agents import job_store
from cogniv_vault.agents.runner import run_graph
from cogniv_vault.api.errors import error_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None


@router.post("", status_code=202)
async def submit_query(req: QueryRequest) -> JSONResponse:
    if not req.question.strip():
        return error_response("invalid_request", "question is required", status=400)

    job_id = str(uuid.uuid4())
    try:
        result = await run_graph(req.question, req.document_ids)
    except Exception as exc:
        logger.exception("agent graph failed")
        return error_response("agent_failed", str(exc), status=500)

    job_store.put(job_id, result)
    return JSONResponse(status_code=202, content={"job_id": job_id})


@router.get("/{job_id}")
async def get_query_result(job_id: str) -> JSONResponse:
    result = job_store.pop(job_id)
    if result is None:
        return error_response("not_found", "no result for job_id", status=404)
    return JSONResponse(status_code=200, content=result)
