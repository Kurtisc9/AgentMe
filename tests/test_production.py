from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.config import Settings
from app.middleware.auth import ApiKeyAuthMiddleware
from app.middleware.error_logging import StructuredExceptionMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware


def test_production_rejects_default_api_key() -> None:
    with pytest.raises(ValueError):
        Settings(environment="production", api_key="replace_me")


def test_production_accepts_custom_api_key() -> None:
    settings = Settings(environment="production", api_key="super-secret-key")

    assert settings.api_key == "super-secret-key"


def test_security_headers_are_added() -> None:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/test")
    def test_route() -> dict[str, bool]:
        return {"ok": True}

    response = TestClient(app).get("/test")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_structured_exception_logging(tmp_path: Path) -> None:
    log_path = tmp_path / "errors.jsonl"
    app = FastAPI()
    app.add_middleware(StructuredExceptionMiddleware, log_path=str(log_path))

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    response = TestClient(app).get("/boom")

    assert response.status_code == 500
    assert log_path.exists()
    assert "boom" in log_path.read_text(encoding="utf-8")


def test_rate_limit_blocks_excess_requests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SAGE_RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("SAGE_RATE_LIMIT_WINDOW_SECONDS", "60")

    from app.config import get_settings

    get_settings.cache_clear()
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware)

    @app.get("/limited")
    def limited() -> dict[str, bool]:
        return {"ok": True}

    client = TestClient(app)
    first = client.get("/limited")
    second = client.get("/limited")

    assert first.status_code == 200
    assert second.status_code == 429
    get_settings.cache_clear()
