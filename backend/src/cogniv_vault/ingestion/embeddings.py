"""MiniLM embeddings — 384-dim, CPU, L2-normalized."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from cogniv_vault.config import get_settings

EMBEDDING_DIM = 384


@lru_cache(maxsize=1)
def get_model() -> Any:
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(get_settings().embedding_model)


def embed(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    model = get_model()
    vectors = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return [list(map(float, row)) for row in vectors]
