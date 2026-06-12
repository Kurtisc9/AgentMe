from __future__ import annotations

from app.core.commander import RiskLevel, SageCommander
from app.integrations.base import IntegrationResult
from app.services.approval_service import ApprovalService
from app.services.audit_service import AuditService
from app.services.integration_registry import IntegrationRegistry


class AutomationService:
    def __init__(
        self,
        *,
        registry: IntegrationRegistry | None = None,
        commander: SageCommander | None = None,
        approval_service: ApprovalService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.registry = registry or IntegrationRegistry()
        self.commander = commander or SageCommander()
        self.approval_service = approval_service or ApprovalService()
        self.audit = audit or AuditService()

    def list_integrations(self) -> list[dict[str, object]]:
        return self.registry.list_integrations()

    def execute(
        self,
        *,
        integration_name: str,
        action: str,
        payload: dict[str, object],
        approval_id: str | None = None,
    ) -> IntegrationResult:
        description = f"Run {integration_name} action {action}"
        routed = self.commander.route_task(description)
        approval_verified = False

        if routed.risk_level == RiskLevel.HIGH or routed.blocked:
            result = IntegrationResult(
                integration_name=integration_name,
                action=action,
                success=False,
                output="Automation blocked by Sage safety policy.",
            )
        elif routed.approval_required:
            if not approval_id:
                result = IntegrationResult(
                    integration_name=integration_name,
                    action=action,
                    success=False,
                    output="Automation requires a verified KurtisC approval record.",
                )
            else:
                self.approval_service.get_verified_approval(
                    approval_id=approval_id,
                    task_description=description,
                )
                approval_verified = True
                integration = self.registry.get(integration_name)
                result = integration.execute(action=action, payload=payload)
        else:
            integration = self.registry.get(integration_name)
            result = integration.execute(action=action, payload=payload)

        self.audit.log(
            "automation_execution",
            {
                "integration_name": integration_name,
                "action": action,
                "approval_id": approval_id,
                "approval_verified": approval_verified,
                "risk_level": routed.risk_level.value,
                "blocked": routed.blocked,
                "success": result.success,
            },
        )
        return result
