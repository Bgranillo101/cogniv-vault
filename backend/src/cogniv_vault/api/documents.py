from fastapi import APIRouter, HTTPException, UploadFile

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", status_code=202)
async def upload_document(file: UploadFile) -> dict[str, str]:
    raise HTTPException(status_code=501, detail="ingestion not implemented (Phase 2)")


@router.get("")
async def list_documents() -> dict[str, list[dict[str, str]]]:
    raise HTTPException(status_code=501, detail="listing not implemented (Phase 2)")
