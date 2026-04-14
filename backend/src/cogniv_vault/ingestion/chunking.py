"""Token-aware chunking for MiniLM (256-token cap). Defaults: 220/32."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, TypedDict

from cogniv_vault.config import get_settings

if TYPE_CHECKING:
    from transformers import PreTrainedTokenizerBase


class Chunk(TypedDict):
    ordinal: int
    content: str
    token_count: int


@lru_cache(maxsize=1)
def _tokenizer() -> PreTrainedTokenizerBase:
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(get_settings().embedding_model)


def chunk_text(text: str, window: int = 220, overlap: int = 32) -> list[Chunk]:
    if window <= 0:
        raise ValueError("window must be > 0")
    if not 0 <= overlap < window:
        raise ValueError("overlap must be in [0, window)")

    stripped = text.strip()
    if not stripped:
        return []

    tok = _tokenizer()
    ids: list[int] = tok.encode(stripped, add_special_tokens=False)
    if not ids:
        return []

    stride = window - overlap
    chunks: list[Chunk] = []
    ordinal = 0
    for start in range(0, len(ids), stride):
        slice_ids = ids[start : start + window]
        if not slice_ids:
            break
        decoded = tok.decode(slice_ids, skip_special_tokens=True)
        content = decoded.strip() if isinstance(decoded, str) else " ".join(decoded).strip()
        if content:
            chunks.append(
                Chunk(ordinal=ordinal, content=content, token_count=len(slice_ids))
            )
            ordinal += 1
        if start + window >= len(ids):
            break
    return chunks
