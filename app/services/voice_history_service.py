import json
from pathlib import Path

from app.models.voice_history import VoiceEventType, VoiceHistoryRecord


class VoiceHistoryService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("data/voice_history.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        event_type: VoiceEventType,
        content: str,
        task_id: str | None = None,
    ) -> VoiceHistoryRecord:
        record = VoiceHistoryRecord.create(
            event_type=event_type,
            content=content,
            task_id=task_id,
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
