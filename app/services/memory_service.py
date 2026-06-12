import json
from datetime import UTC, datetime
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
        project: str | None = None,
        importance: int = 3,
        summary: str | None = None,
    ) -> MemoryRecord:
        if not content.strip():
            raise ValueError("Memory content cannot be empty.")

        record = MemoryRecord.create(
            memory_type=memory_type,
            content=content,
            tags=tags,
            project=project,
            importance=importance,
            summary=summary or self.summarize_text(content),
        )
        self._append(record.to_dict())
        return record

    def list_all(self, *, project: str | None = None) -> list[dict[str, object]]:
        records = self._read_all()
        if project:
            records = [record for record in records if record.get("project") == project]
        return sorted(records, key=self.score_memory, reverse=True)

    def get(self, memory_id: str) -> dict[str, object]:
        records = self._read_all()
        record = next((item for item in records if item.get("memory_id") == memory_id), None)
        if record is None:
            raise KeyError("Memory not found.")
        record["access_count"] = int(record.get("access_count", 0)) + 1
        record["last_accessed_at"] = datetime.now(UTC).isoformat()
        self._rewrite(records)
        return record

    def update(
        self,
        *,
        memory_id: str,
        content: str | None = None,
        tags: list[str] | None = None,
        project: str | None = None,
        importance: int | None = None,
    ) -> dict[str, object]:
        records = self._read_all()
        target = next((item for item in records if item.get("memory_id") == memory_id), None)
        if target is None:
            raise KeyError("Memory not found.")

        if content is not None:
            if not content.strip():
                raise ValueError("Memory content cannot be empty.")
            target["content"] = content.strip()
            target["summary"] = self.summarize_text(content)
        if tags is not None:
            target["tags"] = tags
        if project is not None:
            target["project"] = project
        if importance is not None:
            target["importance"] = max(1, min(5, importance))

        self._rewrite(records)
        return target

    def delete(self, memory_id: str) -> None:
        records = self._read_all()
        filtered = [item for item in records if item.get("memory_id") != memory_id]
        if len(filtered) == len(records):
            raise KeyError("Memory not found.")
        self._rewrite(filtered)

    def search(self, query: str, *, project: str | None = None) -> list[dict[str, object]]:
        normalized = query.strip().lower()
        if not normalized:
            return []

        results = []
        for record in self._read_all():
            if project and record.get("project") != project:
                continue
            haystack = " ".join(
                [
                    str(record.get("content", "")),
                    str(record.get("summary", "")),
                    str(record.get("project", "")),
                    " ".join(str(tag) for tag in record.get("tags", [])),
                ]
            ).lower()
            if normalized in haystack:
                record["score"] = self.score_memory(record) + 2
                results.append(record)
        return sorted(results, key=lambda item: float(item.get("score", 0)), reverse=True)

    def summarize_project(self, project: str) -> dict[str, object]:
        memories = self.list_all(project=project)
        combined = " ".join(str(memory.get("summary") or memory.get("content", "")) for memory in memories[:10])
        return {
            "project": project,
            "memory_count": len(memories),
            "summary": self.summarize_text(combined) if combined else "No memories found.",
            "top_memories": memories[:5],
        }

    def decay_low_value_memories(self) -> int:
        records = self._read_all()
        changed = 0
        for record in records:
            access_count = int(record.get("access_count", 0))
            importance = int(record.get("importance", 3))
            if access_count == 0 and importance > 1:
                record["importance"] = importance - 1
                changed += 1
        if changed:
            self._rewrite(records)
        return changed

    def score_memory(self, record: dict[str, object]) -> float:
        importance = int(record.get("importance", 3))
        access_count = int(record.get("access_count", 0))
        tag_bonus = min(len(record.get("tags", [])), 5) * 0.2
        project_bonus = 0.5 if record.get("project") else 0.0
        return importance + min(access_count, 10) * 0.1 + tag_bonus + project_bonus

    @staticmethod
    def summarize_text(text: str, max_chars: int = 220) -> str:
        normalized = " ".join(text.strip().split())
        if len(normalized) <= max_chars:
            return normalized
        return normalized[: max_chars - 3].rstrip() + "..."

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
                    record = json.loads(stripped)
                    record.setdefault("project", None)
                    record.setdefault("importance", 3)
                    record.setdefault("access_count", 0)
                    record.setdefault("last_accessed_at", None)
                    record.setdefault("summary", self.summarize_text(str(record.get("content", ""))))
                    records.append(record)
        return records

    def _rewrite(self, records: list[dict[str, object]]) -> None:
        with self.path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, default=str) + "\n")
