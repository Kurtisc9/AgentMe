from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class VoiceEventType(StrEnum):
    TRANSCRIPTION = "TRANSCRIPTION"
    SPEECH = "SPEECH"
    COMMAND = "COMMAND"


@dataclass(slots=True)
class VoiceHistoryRecord:
    event_id: str
    event_type: VoiceEventType
    content: str
    created_at: str
    task_id: str | None = None

    @classmethod
    def create(
        cls,
        *,
        event_type: VoiceEventType,
        content: str,
        task_id: str | None = None,
    ) -> "VoiceHistoryRecord":
        return cls(
            event_id=str(uuid4()),
            event_type=event_type,
            content=content,
            created_at=datetime.now(UTC).isoformat(),
            task_id=task_id,
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
