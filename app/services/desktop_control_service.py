from __future__ import annotations

import subprocess
from pathlib import Path

from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.desktop_profile_service import DesktopProfile, DesktopProfileService


class DesktopControlService:
    def __init__(
        self,
        *,
        profiles: DesktopProfileService | None = None,
        approvals: ApprovalService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.profiles = profiles or DesktopProfileService()
        self.approvals = approvals or ApprovalService()
        self.audit = audit or AuditService()

    def list_profiles(self) -> list[dict[str, object]]:
        return [profile.to_dict() for profile in self.profiles.list_profiles()]

    def execute(self, *, profile_id: str, approval_id: str | None = None) -> dict[str, object]:
        profile = self.profiles.get_profile(profile_id)
        description = f"Run desktop profile {profile.id}"

        if profile.risk_level == "HIGH":
            result = self._result(profile, False, "Desktop profile blocked by safety policy.")
        elif profile.risk_level == "MEDIUM":
            if not approval_id:
                result = self._result(profile, False, "Desktop profile requires KurtisC approval.")
            else:
                self.approvals.get_verified_approval(
                    approval_id=approval_id,
                    task_description=description,
                )
                result = self._run(profile)
        else:
            result = self._run(profile)

        self.audit.log(
            "desktop_profile_execution",
            {
                "profile_id": profile.id,
                "profile_type": profile.type,
                "risk_level": profile.risk_level,
                "approval_id": approval_id,
                "success": result["success"],
            },
        )
        return result

    def _run(self, profile: DesktopProfile) -> dict[str, object]:
        try:
            if profile.type == "application":
                subprocess.Popen([profile.command, *profile.arguments])
            elif profile.type == "folder":
                subprocess.Popen(["explorer", str(Path(profile.command).resolve())])
            elif profile.type == "uri":
                subprocess.Popen(["cmd", "/c", "start", "", profile.command], shell=False)
            elif profile.type == "powershell":
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", profile.command],
                    check=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            else:
                raise ValueError(f"Unsupported desktop profile type: {profile.type}")
        except (OSError, subprocess.SubprocessError, ValueError) as exc:
            return self._result(profile, False, str(exc))

        return self._result(profile, True, f"Executed {profile.name}.")

    @staticmethod
    def _result(profile: DesktopProfile, success: bool, output: str) -> dict[str, object]:
        return {
            "profile_id": profile.id,
            "profile_name": profile.name,
            "profile_type": profile.type,
            "risk_level": profile.risk_level,
            "success": success,
            "output": output,
        }
