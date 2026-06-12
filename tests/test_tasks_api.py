from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_route_task_api() -> None:
    response = client.post(
        "/tasks/route",
        json={"description": "Review this Python code"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["assigned_agent"] == "CodeForge"
    assert payload["risk_level"] == "LOW"
    assert payload["approval_required"] is False
    assert payload["blocked"] is False


def test_route_high_risk_task_is_blocked() -> None:
    response = client.post(
        "/tasks/route",
        json={"description": "Transfer money to another account"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["risk_level"] == "HIGH"
    assert payload["blocked"] is True
