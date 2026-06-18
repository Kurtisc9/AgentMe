from __future__ import annotations

from pathlib import Path

from app.services.approval_service import ApprovalService
from app.services.memory_service import MemoryService
from app.services.task_service import TaskService
from app.services.voice_history_service import VoiceHistoryService


class MissionControlService:
    def __init__(
        self,
        *,
        tasks: TaskService | None = None,
        approvals: ApprovalService | None = None,
        memories: MemoryService | None = None,
        voice_history: VoiceHistoryService | None = None,
    ) -> None:
        self.tasks = tasks or TaskService()
        self.approvals = approvals or ApprovalService()
        self.memories = memories or MemoryService()
        self.voice_history = voice_history or VoiceHistoryService()

    def summary(self) -> dict[str, object]:
        task_records = self.tasks.list_tasks()
        approval_records = self.approvals.list_all()
        memory_records = self.memories.list_all()
        voice_events = self.voice_history.list_all()

        return {
            "tasks_total": len(task_records),
            "approvals_total": len(approval_records),
            "approvals_pending": sum(
                1 for item in approval_records if str(item.get("status")) == "PENDING"
            ),
            "memories_total": len(memory_records),
            "voice_events_total": len(voice_events),
            "audit_log_exists": Path("logs/audit.jsonl").exists(),
            "model_metrics_exists": Path("logs/model_metrics.jsonl").exists(),
        }
