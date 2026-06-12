from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.services.embedding_service import EmbeddingService
from app.services.memory_manager import MemoryManager
from app.services.memory_service import MemoryService


client = TestClient(app)


def test_memory_crud_api(tmp_path: Path, monkeypatch) -> None:
    from app.api import memory as memory_api

    local_service = MemoryService(tmp_path / "memories.jsonl")
    monkeypatch.setattr(memory_api, "service", local_service)
    monkeypatch.setattr(
        memory_api,
        "manager",
        MemoryManager(
            local_store=local_service,
            fallback_embedder=EmbeddingService(dimensions=16),
        ),
    )

    created = client.post(
        "/memory",
        json={
            "memory_type": "PROJECT",
            "content": "Build Sage memory API tests.",
            "tags": ["phase-3"],
        },
    )
    assert created.status_code == 201
    memory_id = created.json()["memory_id"]

    fetched = client.get(f"/memory/{memory_id}")
    assert fetched.status_code == 200

    updated = client.patch(
        f"/memory/{memory_id}",
        json={"content": "Updated Sage memory test.", "tags": ["tested"]},
    )
    assert updated.status_code == 200
    assert updated.json()["tags"] == ["tested"]

    deleted = client.delete(f"/memory/{memory_id}")
    assert deleted.status_code == 204
