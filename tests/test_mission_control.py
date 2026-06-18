from pathlib import Path

from app.services.mission_control import MissionControlService
from app.services.task_service import TaskService


class FakeTaskService:
    def list_all(self):
        return ["task-1"]

    def list_tasks(self):
        return ["task-1"]


class FakeApprovalService:
    def list_all(self):
        return [{"status": "PENDING"}, {"status": "APPROVED"}]


class FakeMemoryService:
    def list_all(self):
        return ["m1", "m2"]


class FakeVoiceHistoryService:
    def list_all(self):
        return ["v1"]


def test_mission_control_summary_counts_items(tmp_path: Path) -> None:
    service = MissionControlService(
        tasks=FakeTaskService(),
        approvals=FakeApprovalService(),
        memories=FakeMemoryService(),
        voice_history=FakeVoiceHistoryService(),
    )

    summary = service.summary()

    assert summary["tasks_total"] == 1
    assert summary["approvals_total"] == 2
    assert summary["approvals_pending"] == 1
    assert summary["memories_total"] == 2
    assert summary["voice_events_total"] == 1
