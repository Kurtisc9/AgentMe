from pathlib import Path

import pytest

from app.integrations.base import IntegrationResult
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.automation_service import AutomationService
from app.services.integration_registry import IntegrationRegistry


class FakeIntegration:
    name = "fake"
    description = "Fake integration"
    actions = ("run",)

    def execute(self, *, action: str, payload: dict[str, object]) -> IntegrationResult:
        return IntegrationResult(
            integration_name=self.name,
            action=action,
            success=True,
            output="executed",
        )


def build_service(tmp_path: Path) -> tuple[AutomationService, ApprovalService]:
    approval_service = ApprovalService(tmp_path / "approvals.jsonl")
    service = AutomationService(
        registry=IntegrationRegistry({"fake": FakeIntegration()}),
        approval_service=approval_service,
        audit=AuditService(tmp_path / "audit.jsonl"),
    )
    return service, approval_service


def test_unapproved_automation_is_rejected(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path)

    result = service.execute(
        integration_name="fake",
        action="run",
        payload={},
    )

    assert result.success is False
    assert "verified KurtisC approval" in result.output


def test_execute_action_requires_verified_approval(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path)

    result = service.execute(
        integration_name="fake",
        action="execute",
        payload={},
    )

    assert result.success is False
    assert "verified KurtisC approval" in result.output


def test_matching_approved_record_allows_execution(tmp_path: Path) -> None:
    service, approvals = build_service(tmp_path)
    created = approvals.create(
        task_id="task-1",
        task_description="Run fake action run",
    )
    approvals.decide(
        approval_id=created.approval_id,
        approver_role="KurtisC",
        approve=True,
    )

    result = service.execute(
        integration_name="fake",
        action="run",
        payload={},
        approval_id=created.approval_id,
    )

    assert result.success is True
    assert result.output == "executed"


def test_unrelated_approval_cannot_be_reused(tmp_path: Path) -> None:
    service, approvals = build_service(tmp_path)
    created = approvals.create(
        task_id="task-2",
        task_description="Run other action different",
    )
    approvals.decide(
        approval_id=created.approval_id,
        approver_role="KurtisC",
        approve=True,
    )

    with pytest.raises(PermissionError):
        service.execute(
            integration_name="fake",
            action="run",
            payload={},
            approval_id=created.approval_id,
        )
