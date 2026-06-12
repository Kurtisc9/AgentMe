from app.core.commander import RoutedTask, SageCommander
from app.models.task_record import TaskRecord
from app.services.inbox_service import InboxService


class TaskService:
    def __init__(
        self,
        commander: SageCommander | None = None,
        inbox: InboxService | None = None,
    ) -> None:
        self.commander = commander or SageCommander()
        self.inbox = inbox or InboxService()

    def route(self, description: str) -> TaskRecord:
        routed: RoutedTask = self.commander.route_task(description)
        record = TaskRecord.create(
            description=routed.description,
            assigned_agent=routed.assigned_agent,
            risk_level=routed.risk_level,
            approval_required=routed.approval_required,
            blocked=routed.blocked,
            reason=routed.reason,
        )
        self.inbox.append(record)
        return record

    def list_tasks(self) -> list[dict[str, object]]:
        return self.inbox.list_tasks()
