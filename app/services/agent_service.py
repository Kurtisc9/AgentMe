from __future__ import annotations

from app.agents.base import AgentResult
from app.services.agent_registry import AgentRegistry


class AgentService:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or AgentRegistry()

    def list_agents(self) -> list[dict[str, object]]:
        return self.registry.list_agents()

    def execute(self, *, agent_name: str, task: str) -> AgentResult:
        agent = self.registry.get(agent_name)
        return agent.execute(task)
