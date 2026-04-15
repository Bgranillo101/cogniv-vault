"""Thin async wrapper over the sync Groq SDK."""

from __future__ import annotations

import asyncio
from functools import lru_cache
from typing import Any

from groq import Groq

from cogniv_vault.config import get_settings


@lru_cache(maxsize=1)
def get_client() -> Groq:
    settings = get_settings()
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY must be set")
    return Groq(api_key=settings.groq_api_key)


async def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.2,
    response_format: dict[str, str] | None = None,
) -> str:
    settings = get_settings()
    kwargs: dict[str, Any] = {
        "model": model or settings.groq_model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format

    def _call() -> str:
        resp = get_client().chat.completions.create(**kwargs)
        content = resp.choices[0].message.content
        return content or ""

    return await asyncio.to_thread(_call)
