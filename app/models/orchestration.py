from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(slots=True)
class OrchestrationStep:
    step_id: str
    agent_name: str
    task: str
    success: bool
    output: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class OrchestrationRun:
    run_id: str
    objective: str
    status: str
    steps: list[OrchestrationStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @classmethod
    def create(cls, objective: str) -> "OrchestrationRun":
        return cls(
            run_id=f"orch_{uuid4().hex}",
            objective=objective,
            status="RUNNING",
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "objective": self.objective,
            "status": self.status,
            "steps": [step.to_dict() for step in self.steps],
            "created_at": self.created_at,
        }
