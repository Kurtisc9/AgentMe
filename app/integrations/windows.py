from __future__ import annotations

import subprocess

from app.integrations.base import BaseIntegration, IntegrationResult


class WindowsIntegration(BaseIntegration):
    name = "windows"
    description = "Controlled Windows desktop actions through PowerShell."
    actions = ("open_application",)

    def execute(self, *, action: str, payload: dict[str, object]) -> IntegrationResult:
        if action not in self.actions:
            raise ValueError(f"Unsupported Windows action: {action}")

        application = str(payload.get("application", "")).strip()
        if not application:
            raise ValueError("application is required.")

        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Start-Process", application],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or "Windows action failed.")

        return IntegrationResult(
            integration_name=self.name,
            action=action,
            success=True,
            output=f"Opened {application}.",
        )
