from pathlib import Path

from app.agents.base import AgentResult
from app.services.orchestration_planner import OrchestrationPlanner
from app.services.orchestration_service import OrchestrationService


class FakeAgentService:
    def execute(self, *, agent_name: str, task: str) -> AgentResult:
        return AgentResult(
            agent_name=agent_name,
            task=task,
            output=f"{agent_name} completed",
            success=True,
        )


class BlockingAgentService:
    def execute(self, *, agent_name: str, task: str) -> AgentResult:
        return AgentResult(
            agent_name=agent_name,
            task=task,
            output="blocked",
            success=False,
        )


class FakeAudit:
    def log(self, event_type: str, payload: dict[str, object]) -> None:
        return None


def test_planner_assigns_code_and_design_agents() -> None:
    plan = OrchestrationPlanner().plan("Build app code and design brand logo")
    agents = {step["agent_name"] for step in plan}

    assert "CodeForge" in agents
    assert "VisionForge" in agents


def test_orchestration_completes_successfully(tmp_path: Path) -> None:
    service = OrchestrationService(
        path=tmp_path / "runs.jsonl",
        agents=FakeAgentService(),
        audit=FakeAudit(),
    )

    result = service.run("Write a summary document")

    assert result["status"] == "COMPLETED"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["agent_name"] == "WordForge"


def test_orchestration_blocks_on_failed_step(tmp_path: Path) -> None:
    service = OrchestrationService(
        path=tmp_path / "runs.jsonl",
        agents=BlockingAgentService(),
        audit=FakeAudit(),
    )

    result = service.run("Build app code")

    assert result["status"] == "BLOCKED"
    assert result["steps"][0]["success"] is False


def test_orchestration_history_is_saved(tmp_path: Path) -> None:
    service = OrchestrationService(
        path=tmp_path / "runs.jsonl",
        agents=FakeAgentService(),
        audit=FakeAudit(),
    )

    service.run("Write a summary")
    runs = service.list_runs()

    assert len(runs) == 1
    assert runs[0]["status"] == "COMPLETED"
