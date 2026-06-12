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
        self._append(record.to_dict())
        return record

    def list_all(self) -> list[dict[str, object]]:
        return self._read_all()

    def get(self, memory_id: str) -> dict[str, object]:
        record = next(
            (item for item in self._read_all() if item.get("memory_id") == memory_id),
            None,
        )
        if record is None:
            raise KeyError("Memory not found.")
        return record

    def update(
        self,
        *,
        memory_id: str,
        content: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, object]:
        records = self._read_all()
        target = next((item for item in records if item.get("memory_id") == memory_id), None)
        if target is None:
            raise KeyError("Memory not found.")

        if content is not None:
            if not content.strip():
                raise ValueError("Memory content cannot be empty.")
            target["content"] = content.strip()
        if tags is not None:
            target["tags"] = tags

        self._rewrite(records)
        return target

    def delete(self, memory_id: str) -> None:
        records = self._read_all()
        filtered = [item for item in records if item.get("memory_id") != memory_id]
        if len(filtered) == len(records):
            raise KeyError("Memory not found.")
        self._rewrite(filtered)

    def search(self, query: str) -> list[dict[str, object]]:
        normalized = query.strip().lower()
        if not normalized:
            return []

        return [
            record
            for record in self._read_all()
            if normalized in str(record.get("content", "")).lower()
            or any(normalized in str(tag).lower() for tag in record.get("tags", []))
        ]

    def _append(self, record: dict[str, object]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")

    def _read_all(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []

        records: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def _rewrite(self, records: list[dict[str, object]]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, default=str) + "\n")
