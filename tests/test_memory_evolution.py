from pathlib import Path

from app.models.memory_record import MemoryType
from app.services.memory_service import MemoryService


def test_memory_create_stores_project_importance_and_summary(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")

    record = service.create(
        memory_type=MemoryType.PROJECT,
        content="Elite Clutch needs a tournament leaderboard and membership dashboard.",
        tags=["elite-clutch", "dashboard"],
        project="Elite Clutch",
        importance=5,
    )

    assert record.project == "Elite Clutch"
    assert record.importance == 5
    assert record.summary is not None


def test_memory_search_ranks_by_importance(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")
    service.create(
        memory_type=MemoryType.NOTE,
        content="Sage desktop command center",
        tags=["sage"],
        importance=1,
    )
    important = service.create(
        memory_type=MemoryType.NOTE,
        content="Sage desktop command center critical profile",
        tags=["sage"],
        importance=5,
    )

    results = service.search("desktop")

    assert results[0]["memory_id"] == important.memory_id


def test_get_memory_updates_access_metadata(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")
    record = service.create(
        memory_type=MemoryType.NOTE,
        content="Track PC1 command grid",
    )

    fetched = service.get(record.memory_id)

    assert fetched["access_count"] == 1
    assert fetched["last_accessed_at"] is not None


def test_project_summary_returns_top_memories(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")
    service.create(
        memory_type=MemoryType.PROJECT,
        content="SPD suite needs productivity analytics.",
        project="SPD",
        importance=5,
    )
    service.create(
        memory_type=MemoryType.PROJECT,
        content="SPD suite needs training tracker.",
        project="SPD",
        importance=4,
    )

    summary = service.summarize_project("SPD")

    assert summary["memory_count"] == 2
    assert len(summary["top_memories"]) == 2
    assert "SPD" == summary["project"]


def test_decay_reduces_unused_memory_importance(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")
    record = service.create(
        memory_type=MemoryType.NOTE,
        content="Unused memory",
        importance=5,
    )

    changed = service.decay_low_value_memories()
    updated = service.get(record.memory_id)

    assert changed == 1
    assert updated["importance"] == 4
