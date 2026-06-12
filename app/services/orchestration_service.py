from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.models.orchestration import OrchestrationRun, OrchestrationStep
from app.services.agent_service import AgentService
from app.services.audit_service import AuditService
from app.services.orchestration_planner import OrchestrationPlanner


class OrchestrationService:
    def __init__(
        self,
        *,
        path: Path | None = None,
        planner: OrchestrationPlanner | None = None,
        agents: AgentService | None = None,
        audit: AuditService | None = None,
    ) -> None:
        self.path = path or Path("data/orchestrations.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.planner = planner or OrchestrationPlanner()
        self.agents = agents or AgentService()
        self.audit = audit or AuditService()

    def run(self, objective: str) -> dict[str, object]:
        orchestration = OrchestrationRun.create(objective)
        plan = self.planner.plan(objective)

        for planned_step in plan:
            agent_name = planned_step["agent_name"]
            task = planned_step["task"]
            result = self.agents.execute(agent_name=agent_name, task=task)
            orchestration.steps.append(
                OrchestrationStep(
                    step_id=f"step_{uuid4().hex}",
                    agent_name=agent_name,
                    task=task,
                    success=result.success,
                    output=result.output,
                )
            )
            if not result.success:
                orchestration.status = "BLOCKED"
                break
        else:
            orchestration.status = "COMPLETED"

        self._append(orchestration)
        self.audit.log(
            "orchestration_run",
            {
                "run_id": orchestration.run_id,
                "objective": objective,
                "status": orchestration.status,
                "steps": len(orchestration.steps),
            },
        )
        return orchestration.to_dict()

    def list_runs(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        records: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))
        return records

    def _append(self, orchestration: OrchestrationRun) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(orchestration.to_dict()) + "\n")
