from __future__ import annotations

from collections.abc import Callable

from app.models.memory_record import MemoryRecord, MemoryType
from app.services.embedding_service import EmbeddingService
from app.services.memory_service import MemoryService


class MemoryManager:
    def __init__(
        self,
        *,
        local_store: MemoryService | None = None,
        primary_embedder: object | None = None,
        fallback_embedder: EmbeddingService | None = None,
        vector_upsert: Callable[[MemoryRecord, list[float]], None] | None = None,
    ) -> None:
        self.local_store = local_store or MemoryService()
        self.primary_embedder = primary_embedder
        self.fallback_embedder = fallback_embedder or EmbeddingService()
        self.vector_upsert = vector_upsert

    def create(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        tags: list[str] | None = None,
        project: str | None = None,
        importance: int = 3,
    ) -> tuple[MemoryRecord, str]:
        record = self.local_store.create(
            memory_type=memory_type,
            content=content,
            tags=tags,
            project=project,
            importance=importance,
        )
        vector, provider = self._embed_with_fallback(content)

        if self.vector_upsert is not None:
            self.vector_upsert(record, vector)

        return record, provider

    def _embed_with_fallback(self, text: str) -> tuple[list[float], str]:
        if self.primary_embedder is not None:
            try:
                vector = self.primary_embedder.embed(text)
                return vector, self.primary_embedder.__class__.__name__
            except (RuntimeError, ValueError, OSError):
                pass
            except Exception:
                pass

        return self.fallback_embedder.embed(text), self.fallback_embedder.__class__.__name__
