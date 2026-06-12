from pathlib import Path

from app.services.inbox_service import InboxService
from app.services.task_service import TaskService


def test_routed_task_is_saved_to_inbox(tmp_path: Path) -> None:
    inbox = InboxService(tmp_path / "tasks.jsonl")
    service = TaskService(inbox=inbox)

    record = service.route("Review this Python code")
    tasks = inbox.list_tasks()

    assert len(tasks) == 1
    assert tasks[0]["task_id"] == record.task_id
    assert tasks[0]["assigned_agent"] == "CodeForge"
