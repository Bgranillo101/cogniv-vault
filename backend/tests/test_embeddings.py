import math

from cogniv_vault.ingestion.embeddings import EMBEDDING_DIM, embed


def test_empty_input() -> None:
    assert embed([]) == []


def test_single_vector_shape_and_norm() -> None:
    [vec] = embed(["hello world"])
    assert len(vec) == EMBEDDING_DIM == 384
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-4


def test_batch_shape() -> None:
    batch = embed(["one", "two", "three"])
    assert len(batch) == 3
    assert all(len(v) == 384 for v in batch)
