from __future__ import annotations

import httpx

from app.integrations.base import BaseIntegration, IntegrationResult


class N8NIntegration(BaseIntegration):
    name = "n8n"
    description = "Trigger approved automation workflows through n8n webhooks."
    actions = ("trigger_webhook",)

    def __init__(self, base_url: str = "http://127.0.0.1:5678") -> None:
        self.base_url = base_url.rstrip("/")

    def execute(self, *, action: str, payload: dict[str, object]) -> IntegrationResult:
        if action not in self.actions:
            raise ValueError(f"Unsupported n8n action: {action}")

        webhook_path = str(payload.get("webhook_path", "")).strip().lstrip("/")
        if not webhook_path:
            raise ValueError("n8n webhook_path is required.")

        response = httpx.post(
            f"{self.base_url}/webhook/{webhook_path}",
            json=payload.get("data", {}),
            timeout=30.0,
        )
        response.raise_for_status()

        return IntegrationResult(
            integration_name=self.name,
            action=action,
            success=True,
            output=response.text or "n8n workflow triggered.",
        )
