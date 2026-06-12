import json
from pathlib import Path

from app.models.memory_record import MemoryRecord, MemoryType


class MemoryService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("data/memories.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def create(
        self,
        *,
        memory_type: MemoryType,
        content: str,
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        if not content.strip():
            raise ValueError("Memory content cannot be empty.")

        record = MemoryRecord.create(
            memory_type=memory_type,
            content=content,
            tags=tags,
        )
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), default=str) + "\n")
        return record

    def list_all(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []

        records: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def search(self, query: str) -> list[dict[str, object]]:
        normalized = query.strip().lower()
        if not normalized:
            return []

        return [
            record
            for record in self.list_all()
            if normalized in str(record.get("content", "")).lower()
            or any(normalized in str(tag).lower() for tag in record.get("tags", []))
        ]
