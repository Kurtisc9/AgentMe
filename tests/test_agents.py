from pathlib import Path

from app.services.agent_service import AgentService
from app.services.audit_service import AuditService
from app.services.memory_service import MemoryService


def build_service(tmp_path: Path) -> AgentService:
    return AgentService(
        memory=MemoryService(tmp_path / "memories.jsonl"),
        audit=AuditService(tmp_path / "audit.jsonl"),
    )


def test_low_risk_agent_task_executes(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    result = service.execute(
        agent_name="CodeForge",
        task="Review this Python code",
    )

    assert result.success is True
    assert result.agent_name == "CodeForge"


def test_medium_risk_agent_task_requires_approval(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    result = service.execute(
        agent_name="CodeForge",
        task="Edit file for the React dashboard",
    )

    assert result.success is False
    assert "requires KurtisC approval" in result.output


def test_high_risk_agent_task_is_blocked(tmp_path: Path) -> None:
    service = build_service(tmp_path)

    result = service.execute(
        agent_name="FinanceForge",
        task="Transfer money to another account",
    )

    assert result.success is False
    assert "blocked" in result.output.lower()


def test_successful_agent_execution_writes_memory(tmp_path: Path) -> None:
    memory = MemoryService(tmp_path / "memories.jsonl")
    service = AgentService(
        memory=memory,
        audit=AuditService(tmp_path / "audit.jsonl"),
    )

    service.execute(agent_name="WordForge", task="Write a project summary")

    records = memory.list_all()
    assert len(records) == 1
    assert "WordForge completed" in str(records[0]["content"])
