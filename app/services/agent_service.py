from __future__ import annotations

from app.agents.base import AgentResult
from app.core.commander import RiskLevel, SageCommander
from app.models.memory_record import MemoryType
from app.services.agent_registry import AgentRegistry
from app.services.audit_service import AuditService
from app.services.memory_service import MemoryService
from app.services.model_execution import ModelExecutionService


AGENT_TASK_TYPES = {
    "CodeForge": "code",
    "VisionForge": "general",
    "PhotoForge": "general",
    "MotionForge": "general",
    "WordForge": "writing",
    "FinanceForge": "analysis",
    "MarketForge": "analysis",
}


class AgentService:
    def __init__(
        self,
        registry: AgentRegistry | None = None,
        commander: SageCommander | None = None,
        memory: MemoryService | None = None,
        audit: AuditService | None = None,
        model_execution: ModelExecutionService | None = None,
    ) -> None:
        self.registry = registry or AgentRegistry()
        self.commander = commander or SageCommander()
        self.memory = memory or MemoryService()
        self.audit = audit or AuditService()
        self.model_execution = model_execution or ModelExecutionService()

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
            task_type = AGENT_TASK_TYPES.get(agent_name, "general")
            prompt = (
                f"You are {agent.name}. {agent.description}\n"
                f"Task: {task}\n"
                "Return a precise, useful result without claiming actions you did not perform."
            )
            try:
                model, output, fallback_used = self.model_execution.generate(
                    task_type=task_type,
                    prompt=prompt,
                )
                result = AgentResult(
                    agent_name=agent_name,
                    task=task,
                    output=output,
                    success=True,
                )
            except RuntimeError:
                fallback_used = False
                model = None
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
                "model_name": model.name if "model" in locals() and model else None,
                "fallback_used": fallback_used if "fallback_used" in locals() else False,
            },
        )

        if result.success:
            self.memory.create(
                memory_type=MemoryType.NOTE,
                content=f"{agent_name} completed: {task}",
                tags=["agent", agent_name.lower()],
            )

        return result
