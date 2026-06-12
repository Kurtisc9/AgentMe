from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class IntegrationResult:
    integration_name: str
    action: str
    success: bool
    output: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class BaseIntegration(ABC):
    name: str
    description: str
    actions: tuple[str, ...]

    @abstractmethod
    def execute(self, *, action: str, payload: dict[str, object]) -> IntegrationResult:
        raise NotImplementedError
