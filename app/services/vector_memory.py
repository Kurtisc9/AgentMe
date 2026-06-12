from __future__ import annotations

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.models.memory_record import MemoryRecord
from app.services.embedding_service import EmbeddingService


class VectorMemoryStore:
    def __init__(
        self,
        url: str,
        *,
        collection_name: str = "agentme_memories",
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        self.client = QdrantClient(url=url)
        self.collection_name = collection_name
        self.embedding_service = embedding_service or EmbeddingService()

    def initialize(self) -> None:
        collections = {item.name for item in self.client.get_collections().collections}
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_service.dimensions,
                    distance=Distance.COSINE,
                ),
            )

    def upsert(self, record: MemoryRecord) -> None:
        vector = self.embedding_service.embed(record.content)
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=record.memory_id,
                    vector=vector,
                    payload=record.to_dict(),
                )
            ],
        )

    def search(self, query: str, limit: int = 5) -> list[dict[str, object]]:
        vector = self.embedding_service.embed(query)
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            limit=limit,
        )
        return [
            {
                "score": result.score,
                **(result.payload or {}),
            }
            for result in results
        ]
