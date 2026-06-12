from fastapi.testclient import TestClient

from app.main import app
from app.services.approval_service import ApprovalService


client = TestClient(app)


def test_approval_list_endpoint() -> None:
    response = client.get("/approvals")

    assert response.status_code == 200
    assert "approvals" in response.json()


def test_approval_requires_kurtisc_role(tmp_path, monkeypatch) -> None:
    service = ApprovalService(tmp_path / "approvals.jsonl")
    approval = service.create(task_id="task-1", task_description="Edit file")

    from app.api import approvals as approvals_api

    monkeypatch.setattr(approvals_api, "service", service)

    response = client.post(
        f"/approvals/{approval.approval_id}/approve",
        json={"approver_role": "admin", "note": "Should fail"},
    )

    assert response.status_code == 403


def test_kurtisc_can_approve_via_api(tmp_path, monkeypatch) -> None:
    service = ApprovalService(tmp_path / "approvals.jsonl")
    approval = service.create(task_id="task-1", task_description="Edit file")

    from app.api import approvals as approvals_api

    monkeypatch.setattr(approvals_api, "service", service)

    response = client.post(
        f"/approvals/{approval.approval_id}/approve",
        json={"approver_role": "KurtisC", "note": "Approved"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "APPROVED"
