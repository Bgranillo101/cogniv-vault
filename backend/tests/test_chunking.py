from cogniv_vault.ingestion.chunking import chunk_text


def test_empty_returns_no_chunks() -> None:
    assert chunk_text("") == []
    assert chunk_text("   \n\t") == []


def test_short_text_single_chunk() -> None:
    chunks = chunk_text("hello world")
    assert len(chunks) == 1
    assert chunks[0]["ordinal"] == 0
    assert chunks[0]["token_count"] > 0
    assert chunks[0]["token_count"] <= 220


def test_long_text_windowing() -> None:
    text = " ".join(["lorem ipsum dolor sit amet"] * 300)
    chunks = chunk_text(text, window=220, overlap=32)
    assert len(chunks) >= 2
    assert [c["ordinal"] for c in chunks] == list(range(len(chunks)))
    for c in chunks:
        assert c["token_count"] <= 220
        assert c["content"]
