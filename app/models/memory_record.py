from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class MemoryType(StrEnum):
    PREFERENCE = "PREFERENCE"
    PROJECT = "PROJECT"
    DECISION = "DECISION"
    NOTE = "NOTE"


@dataclass(slots=True)
class MemoryRecord:
    memory_id: str
    memory_type: MemoryType
    content: str
    tags: list[str]
    created_at: str
    project: str | None = None
    importance: int = 3
    access_count: int = 0
    last_accessed_at: str | None = None
    summary: str | None = None

    @classmethod
    def create(
        cls,
        *,
        memory_type: MemoryType,
        content: str,
        tags: list[str] | None = None,
        project: str | None = None,
        importance: int = 3,
        summary: str | None = None,
    ) -> "MemoryRecord":
        return cls(
            memory_id=str(uuid4()),
            memory_type=memory_type,
            content=content.strip(),
            tags=tags or [],
            created_at=datetime.now(UTC).isoformat(),
            project=project,
            importance=max(1, min(5, importance)),
            summary=summary,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
