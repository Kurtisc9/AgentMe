from __future__ import annotations

from app.core.commander import RiskLevel, SageCommander
from app.integrations.base import IntegrationResult
from app.services.audit_service import AuditService
from app.services.integration_registry import IntegrationRegistry


class AutomationService:
    def __init__(
        self,
        *,
        registry: IntegrationRegistry | None = None,
        commander: SageCommander | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.registry = registry or IntegrationRegistry()
        self.commander = commander or SageCommander()
        self.audit = audit or AuditService()

    def list_integrations(self) -> list[dict[str, object]]:
        return self.registry.list_integrations()

    def execute(
        self,
        *,
        integration_name: str,
        action: str,
        payload: dict[str, object],
        approved: bool = False,
    ) -> IntegrationResult:
        description = f"Run {integration_name} action {action}"
        routed = self.commander.route_task(description)

        if routed.risk_level == RiskLevel.HIGH or routed.blocked:
            result = IntegrationResult(
                integration_name=integration_name,
                action=action,
                success=False,
                output="Automation blocked by Sage safety policy.",
            )
        elif routed.approval_required and not approved:
            result = IntegrationResult(
                integration_name=integration_name,
                action=action,
                success=False,
                output="Automation requires KurtisC approval.",
            )
        else:
            integration = self.registry.get(integration_name)
            result = integration.execute(action=action, payload=payload)

        self.audit.log(
            "automation_execution",
            {
                "integration_name": integration_name,
                "action": action,
                "approved": approved,
                "risk_level": routed.risk_level.value,
                "blocked": routed.blocked,
                "success": result.success,
            },
        )
        return result
