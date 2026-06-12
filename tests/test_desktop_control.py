import json
from pathlib import Path

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.desktop_control_service import DesktopControlService
from app.services.desktop_profile_service import DesktopProfile, DesktopProfileService
from app.services.voice_desktop_service import VoiceDesktopService


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
                        "device": "PC1",
                        "favorite": True,
                    },
                    {
                        "id": "medium_action",
                        "name": "Medium Action",
                        "type": "powershell",
                        "risk_level": "MEDIUM",
                        "command": "Write-Output 'ok'",
                        "arguments": [],
                        "device": "PC1",
                        "favorite": False,
                    },
                    {
                        "id": "high_action",
                        "name": "High Action",
                        "type": "powershell",
                        "risk_level": "HIGH",
                        "command": "Write-Output 'blocked'",
                        "arguments": [],
                        "device": "PC2",
                        "favorite": False,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )


def build_service(tmp_path: Path) -> tuple[DesktopControlService, ApprovalService, DesktopProfileService]:
    profile_path = tmp_path / "profiles.json"
    write_profiles(profile_path)
    approvals = ApprovalService(tmp_path / "approvals.jsonl")
    profile_service = DesktopProfileService(profile_path)
    service = DesktopControlService(
        profiles=profile_service,
        approvals=approvals,
        audit=AuditService(tmp_path / "audit.jsonl"),
    )
    return service, approvals, profile_service


def test_profiles_are_loaded(tmp_path: Path) -> None:
    service, _, _ = build_service(tmp_path)

    profiles = service.list_profiles()

    assert len(profiles) == 3
    assert profiles[0]["id"] == "low_action"


def test_profiles_can_filter_by_device(tmp_path: Path) -> None:
    service, _, _ = build_service(tmp_path)

    pc2_profiles = service.list_profiles(device="PC2")

    assert len(pc2_profiles) == 1
    assert pc2_profiles[0]["id"] == "high_action"


def test_profile_editor_upserts_and_deletes(tmp_path: Path) -> None:
    _, _, profiles = build_service(tmp_path)
    profile = DesktopProfile(
        id="new_profile",
        name="New Profile",
        type="uri",
        risk_level="LOW",
        command="ms-settings:display",
        arguments=[],
        device="PC1",
        favorite=True,
    )

    profiles.create_or_update(profile)
    assert profiles.get_profile("new_profile").favorite is True

    profiles.delete("new_profile")
    try:
        profiles.get_profile("new_profile")
    except KeyError:
        pass
    else:
        raise AssertionError("Profile should have been deleted.")


def test_medium_profile_requires_approval(tmp_path: Path) -> None:
    service, _, _ = build_service(tmp_path)

    result = service.execute(profile_id="medium_action")

    assert result["success"] is False
    assert "requires KurtisC approval" in str(result["output"])


def test_high_profile_is_blocked(tmp_path: Path) -> None:
    service, _, _ = build_service(tmp_path)

    result = service.execute(profile_id="high_action")

    assert result["success"] is False
    assert "blocked" in str(result["output"]).lower()


def test_unrelated_approval_is_rejected(tmp_path: Path) -> None:
    service, approvals, _ = build_service(tmp_path)
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


def test_voice_desktop_routes_matching_profile(tmp_path: Path) -> None:
    service, _, profiles = build_service(tmp_path)
    voice_desktop = VoiceDesktopService(desktop=service, profiles=profiles)

    result = voice_desktop.route(text="Sage low action")

    assert result["matched"] is True
    assert result["profile_id"] == "low_action"
