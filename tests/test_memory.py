from pathlib import Path

from app.models.memory_record import MemoryType
from app.services.memory_service import MemoryService


def test_create_and_list_memory(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")

    record = service.create(
        memory_type=MemoryType.PREFERENCE,
        content="Prefer short precise answers.",
        tags=["style", "sage"],
    )

    memories = service.list_all()

    assert len(memories) == 1
    assert memories[0]["memory_id"] == record.memory_id
    assert memories[0]["memory_type"] == "PREFERENCE"


def test_search_memory_by_content_and_tag(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")
    service.create(
        memory_type=MemoryType.PROJECT,
        content="AgentMe uses a Jarvis HUD.",
        tags=["dashboard", "voice"],
    )

    by_content = service.search("Jarvis")
    by_tag = service.search("voice")

    assert len(by_content) == 1
    assert len(by_tag) == 1


def test_empty_memory_is_rejected(tmp_path: Path) -> None:
    service = MemoryService(tmp_path / "memories.jsonl")

    try:
        service.create(memory_type=MemoryType.NOTE, content="   ")
    except ValueError as exc:
        assert str(exc) == "Memory content cannot be empty."
    else:
        raise AssertionError("Expected ValueError")
