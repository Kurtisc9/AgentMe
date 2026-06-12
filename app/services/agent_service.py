from __future__ import annotations

from app.agents.base import AgentResult
from app.core.commander import RiskLevel, SageCommander
from app.models.memory_record import MemoryType
from app.services.agent_registry import AgentRegistry
from app.services.audit_service import AuditService
from app.services.memory_service import MemoryService


class AgentService:
    def __init__(
        self,
        registry: AgentRegistry | None = None,
        commander: SageCommander | None = None,
        memory: MemoryService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.commander = commander or SageCommander()
        self.memory = memory or MemoryService()
        self.audit = audit or AuditService()

    def list_agents(self) -> list[dict[str, object]]:
        return self.registry.list_agents()

    def execute(self, *, agent_name: str, task: str) -> AgentResult:
        routed = self.commander.route_task(task)

        if routed.risk_level == RiskLevel.HIGH or routed.blocked:
            result = AgentResult(
                agent_name=agent_name,
                task=task,
                output="Execution blocked by Sage safety policy.",
                success=False,
            )
        elif routed.approval_required:
            result = AgentResult(
                agent_name=agent_name,
                task=task,
                output="Execution requires KurtisC approval before the agent may proceed.",
                success=False,
            )
        else:
            agent = self.registry.get(agent_name)
            result = agent.execute(task)

        self.audit.log(
            "agent_execution",
            {
                "agent_name": agent_name,
                "task": task,
                "risk_level": routed.risk_level.value,
                "approval_required": routed.approval_required,
                "blocked": routed.blocked,
                "success": result.success,
            },
        )

        if result.success:
            self.memory.create(
                memory_type=MemoryType.NOTE,
                content=f"{agent_name} completed: {task}",
                tags=["agent", agent_name.lower()],
            )

        return result
