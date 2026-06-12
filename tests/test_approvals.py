from pathlib import Path

import pytest

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.inbox_service import InboxService
from app.services.task_service import TaskService


def test_medium_task_creates_approval(tmp_path: Path) -> None:
    approvals = ApprovalService(tmp_path / "approvals.jsonl")
    service = TaskService(
        inbox=InboxService(tmp_path / "tasks.jsonl"),
        approvals=approvals,
        audit=AuditService(tmp_path / "audit.jsonl"),
    )

    task = service.route("Edit file for the React dashboard")
    records = approvals.list_all()

    assert task.approval_required is True
    assert len(records) == 1
    assert records[0]["task_id"] == task.task_id
    assert records[0]["status"] == "PENDING"


def test_only_kurtisc_can_approve(tmp_path: Path) -> None:
    approvals = ApprovalService(tmp_path / "approvals.jsonl")
    approval = approvals.create(task_id="task-1", task_description="Edit file")

    with pytest.raises(PermissionError):
        approvals.decide(
            approval_id=approval.approval_id,
            approver_role="admin",
            approve=True,
        )


def test_kurtisc_can_approve(tmp_path: Path) -> None:
    approvals = ApprovalService(tmp_path / "approvals.jsonl")
    approval = approvals.create(task_id="task-1", task_description="Edit file")

    decided = approvals.decide(
        approval_id=approval.approval_id,
        approver_role="KurtisC",
        approve=True,
        note="Approved for testing.",
    )

    assert decided["status"] == "APPROVED"
    assert decided["decision_note"] == "Approved for testing."
