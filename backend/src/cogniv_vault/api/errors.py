"""Uniform error envelope per docs/API_CONTRACTS.md."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def error_response(
    code: str,
    message: str,
    detail: dict[str, Any] | None = None,
    status: int = 400,
) -> JSONResponse:
    body: dict[str, Any] = {"error": {"code": code, "message": message}}
    if detail is not None:
        body["error"]["detail"] = detail
    return JSONResponse(status_code=status, content=body)
