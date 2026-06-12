from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import uuid4


class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"


@dataclass(slots=True)
class ApprovalRecord:
    approval_id: str
    task_id: str
    task_description: str
    status: ApprovalStatus
    owner_role: str
    created_at: str
    expires_at: str
    decided_at: str | None = None
    decision_note: str | None = None

    @classmethod
    def create(
        cls,
        *,
        task_id: str,
        task_description: str,
        owner_role: str = "KurtisC",
        expiration_hours: int = 24,
    ) -> "ApprovalRecord":
        created = datetime.now(UTC)
        return cls(
            approval_id=str(uuid4()),
            task_id=task_id,
            task_description=task_description,
            status=ApprovalStatus.PENDING,
            owner_role=owner_role,
            created_at=created.isoformat(),
            expires_at=(created + timedelta(hours=expiration_hours)).isoformat(),
        )

    def is_expired(self) -> bool:
        return datetime.now(UTC) >= datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
