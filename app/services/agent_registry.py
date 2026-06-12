from __future__ import annotations

from app.agents.base import BaseAgent
from app.agents.specialists import build_specialists


class AgentRegistry:
    def __init__(self, agents: dict[str, BaseAgent] | None = None) -> None:
        self._agents = agents or build_specialists()

    def list_agents(self) -> list[dict[str, object]]:
        return [
            {
                "name": agent.name,
                "description": agent.description,
                "capabilities": list(agent.capabilities),
            }
            for agent in self._agents.values()
        ]

    def get(self, name: str) -> BaseAgent:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Unknown agent: {name}") from exc
