import json
from datetime import UTC, datetime
from pathlib import Path


class AuditService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("logs/audit.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: str, payload: dict[str, object]) -> None:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "payload": payload,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, default=str) + "\n")
