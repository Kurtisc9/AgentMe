from app.services.embedding_service import EmbeddingService


def test_embedding_is_deterministic() -> None:
    service = EmbeddingService(dimensions=32)

    first = service.embed("Sage remembers project decisions")
    second = service.embed("Sage remembers project decisions")

    assert first == second
    assert len(first) == 32


def test_embedding_rejects_empty_text() -> None:
    service = EmbeddingService()

    try:
        service.embed("   ")
    except ValueError as exc:
        assert str(exc) == "Cannot embed empty text."
    else:
        raise AssertionError("Expected ValueError")
