from app.core.commander import RoutedTask, SageCommander
from app.models.task_record import TaskRecord
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.inbox_service import InboxService


class TaskService:
    def __init__(
        self,
        commander: SageCommander | None = None,
        inbox: InboxService | None = None,
        approvals: ApprovalService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.commander = commander or SageCommander()
        self.inbox = inbox or InboxService()
        self.approvals = approvals or ApprovalService()
        self.audit = audit or AuditService()

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

        approval_id: str | None = None
        if record.approval_required and not record.blocked:
            approval = self.approvals.create(
                task_id=record.task_id,
                task_description=record.description,
            )
            approval_id = approval.approval_id

        self.audit.log(
            "task_routed",
            {
                **record.to_dict(),
                "approval_id": approval_id,
            },
        )
        return record

    def list_tasks(self) -> list[dict[str, object]]:
        return self.inbox.list_tasks()
