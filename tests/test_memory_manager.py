from pathlib import Path

from app.models.memory_record import MemoryType
from app.services.embedding_service import EmbeddingService
from app.services.memory_manager import MemoryManager
from app.services.memory_service import MemoryService


class WorkingEmbedder:
    def embed(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FailingEmbedder:
    def embed(self, text: str) -> list[float]:
        raise RuntimeError("provider offline")


def test_primary_embedding_provider_is_used(tmp_path: Path) -> None:
    manager = MemoryManager(
        local_store=MemoryService(tmp_path / "memories.jsonl"),
        primary_embedder=WorkingEmbedder(),
    )

    _, provider = manager.create(
        memory_type=MemoryType.PROJECT,
        content="Build the Sage HUD.",
    )

    assert provider == "WorkingEmbedder"


def test_fallback_embedding_provider_is_used(tmp_path: Path) -> None:
    fallback = EmbeddingService(dimensions=16)
    manager = MemoryManager(
        local_store=MemoryService(tmp_path / "memories.jsonl"),
        primary_embedder=FailingEmbedder(),
        fallback_embedder=fallback,
    )

    _, provider = manager.create(
        memory_type=MemoryType.DECISION,
        content="Use PostgreSQL for structured memory.",
    )

    assert provider == "EmbeddingService"
