from fastapi import APIRouter, WebSocket

router = APIRouter(tags=["ws"])


@router.websocket("/ws/query/{job_id}")
async def agent_stream(websocket: WebSocket, job_id: str) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "AGENT_ERROR",
            "ts": "1970-01-01T00:00:00Z",
            "payload": {
                "code": "NOT_IMPLEMENTED",
                "message": "agent stream not wired (Phase 4)",
                "stage": "graph",
            },
        }
    )
    await websocket.close()
