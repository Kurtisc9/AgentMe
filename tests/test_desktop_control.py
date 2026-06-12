import json
from pathlib import Path

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.desktop_control_service import DesktopControlService
from app.services.desktop_profile_service import DesktopProfileService


def write_profiles(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "profiles": [
                    {
                        "id": "low_action",
                        "name": "Low Action",
                        "type": "application",
                        "risk_level": "LOW",
                        "command": "missing-app.exe",
                        "arguments": [],
                    },
                    {
                        "id": "medium_action",
                        "name": "Medium Action",
                        "type": "powershell",
                        "risk_level": "MEDIUM",
                        "command": "Write-Output 'ok'",
                        "arguments": [],
                    },
                    {
                        "id": "high_action",
                        "name": "High Action",
                        "type": "powershell",
                        "risk_level": "HIGH",
                        "command": "Write-Output 'blocked'",
                        "arguments": [],
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


def build_service(tmp_path: Path) -> tuple[DesktopControlService, ApprovalService]:
    profile_path = tmp_path / "profiles.json"
    write_profiles(profile_path)
    approvals = ApprovalService(tmp_path / "approvals.jsonl")
    service = DesktopControlService(
        profiles=DesktopProfileService(profile_path),
        approvals=approvals,
        audit=AuditService(tmp_path / "audit.jsonl"),
    )
    return service, approvals


def test_profiles_are_loaded(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path)

    profiles = service.list_profiles()

    assert len(profiles) == 3
    assert profiles[0]["id"] == "low_action"


def test_medium_profile_requires_approval(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path)

    result = service.execute(profile_id="medium_action")

    assert result["success"] is False
    assert "requires KurtisC approval" in str(result["output"])


def test_high_profile_is_blocked(tmp_path: Path) -> None:
    service, _ = build_service(tmp_path)

    result = service.execute(profile_id="high_action")

    assert result["success"] is False
    assert "blocked" in str(result["output"]).lower()


def test_unrelated_approval_is_rejected(tmp_path: Path) -> None:
    service, approvals = build_service(tmp_path)
    created = approvals.create(task_id="task-1", task_description="Run desktop profile another_action")
    approvals.decide(
        approval_id=created.approval_id,
        approver_role="KurtisC",
        approve=True,
    )

    try:
        service.execute(profile_id="medium_action", approval_id=created.approval_id)
    except PermissionError:
        pass
    else:
        raise AssertionError("Unrelated approval should be rejected.")
