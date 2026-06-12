from pydantic import BaseModel, Field

from app.models.approval_record import ApprovalStatus


class ApprovalDecision(BaseModel):
    approver_role: str = Field(min_length=1)
    note: str | None = Field(default=None, max_length=1000)


class ApprovalResponse(BaseModel):
    approval_id: str
    task_id: str
    task_description: str
    status: ApprovalStatus
    owner_role: str
    created_at: str
    expires_at: str
    decided_at: str | None = None
    decision_note: str | None = None


class ApprovalListResponse(BaseModel):
    approvals: list[dict[str, object]]
