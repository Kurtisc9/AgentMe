import json
from pathlib import Path

from app.models.task_record import TaskRecord


class InboxService:
    def __init__(self, inbox_path: Path | None = None) -> None:
        self.inbox_path = inbox_path or Path("Inbox/tasks.jsonl")
        self.inbox_path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, record: TaskRecord) -> None:
        with self.inbox_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.to_dict(), default=str) + "\n")

    def list_tasks(self) -> list[dict[str, object]]:
        if not self.inbox_path.exists():
            return []

        tasks: list[dict[str, object]] = []
        with self.inbox_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    tasks.append(json.loads(stripped))
        return tasks
