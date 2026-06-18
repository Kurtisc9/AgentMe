from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["status"] == "healthy"
    assert payload["service"] == "AgentMe / Sage"


def test_ready_endpoint_reports_unavailable_dependencies() -> None:
    response = client.get("/ready")

    assert response.status_code == 503
    payload = response.json()
    assert payload["detail"]["ready"] is False
    assert set(payload["detail"]["required"]) == {"postgres", "qdrant"}
    assert set(payload["detail"]["providers"]) == {"postgres", "qdrant", "ollama", "lm_studio"}
