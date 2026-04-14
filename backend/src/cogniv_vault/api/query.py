from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None


@router.post("", status_code=202)
async def submit_query(req: QueryRequest) -> dict[str, str]:
    raise HTTPException(status_code=501, detail="agent graph not wired (Phase 3)")
