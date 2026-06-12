from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class AgentResult:
    agent_name: str
    task: str
    output: str
    success: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class BaseAgent(ABC):
    name: str
    description: str
    capabilities: tuple[str, ...]

    @abstractmethod
    def execute(self, task: str) -> AgentResult:
        raise NotImplementedError
