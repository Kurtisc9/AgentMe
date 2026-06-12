from __future__ import annotations

from app.models.memory_record import MemoryRecord
from app.services.vector_memory import VectorMemoryStore


class SemanticMemoryService:
    def __init__(self, vector_store: VectorMemoryStore) -> None:
        self.vector_store = vector_store

    def initialize(self) -> None:
        self.vector_store.initialize()

    def upsert(self, record: MemoryRecord) -> None:
        self.vector_store.upsert(record)

    def search(self, query: str, limit: int = 5) -> list[dict[str, object]]:
        if not query.strip():
            raise ValueError("Semantic search query cannot be empty.")
        if limit < 1 or limit > 25:
            raise ValueError("Semantic search limit must be between 1 and 25.")
        return self.vector_store.search(query, limit=limit)
