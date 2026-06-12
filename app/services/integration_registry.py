from __future__ import annotations

from app.integrations.base import BaseIntegration
from app.integrations.browser import BrowserIntegration
from app.integrations.n8n import N8NIntegration
from app.integrations.windows import WindowsIntegration


class IntegrationRegistry:
    def __init__(self, integrations: dict[str, BaseIntegration] | None = None) -> None:
        self._integrations = integrations or {
            "n8n": N8NIntegration(),
            "browser": BrowserIntegration(),
            "windows": WindowsIntegration(),
        }

    def list_integrations(self) -> list[dict[str, object]]:
        return [
            {
                "name": integration.name,
                "description": integration.description,
                "actions": list(integration.actions),
            }
            for integration in self._integrations.values()
        ]

    def get(self, name: str) -> BaseIntegration:
        try:
            return self._integrations[name]
        except KeyError as exc:
            raise KeyError(f"Unknown integration: {name}") from exc
