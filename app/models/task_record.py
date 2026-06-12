from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4

from app.core.commander import RiskLevel


class TaskStatus(StrEnum):
    RECEIVED = "RECEIVED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ROUTED = "ROUTED"
    BLOCKED = "BLOCKED"


@dataclass(slots=True)
class TaskRecord:
    task_id: str
    description: str
    assigned_agent: str
    risk_level: RiskLevel
    approval_required: bool
    blocked: bool
    reason: str
    status: TaskStatus
    created_at: str

    @classmethod
    def create(
        cls,
        *,
        description: str,
        assigned_agent: str,
        risk_level: RiskLevel,
        approval_required: bool,
        blocked: bool,
        reason: str,
    ) -> "TaskRecord":
        if blocked:
            status = TaskStatus.BLOCKED
        elif approval_required:
            status = TaskStatus.PENDING_APPROVAL
        else:
            status = TaskStatus.ROUTED

        return cls(
            task_id=str(uuid4()),
            description=description,
            assigned_agent=assigned_agent,
            risk_level=risk_level,
            approval_required=approval_required,
            blocked=blocked,
            reason=reason,
            status=status,
            created_at=datetime.now(UTC).isoformat(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
