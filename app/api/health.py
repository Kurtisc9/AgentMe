from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status

from app.services.provider_health import ProviderHealthService


router = APIRouter(tags=["health"])
provider_health = ProviderHealthService()


@router.get("/health")
def health_check() -> dict[str, object]:
    return {
        "ok": True,
        "service": "AgentMe / Sage",
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/ready")
def readiness_check() -> dict[str, object]:
    providers = provider_health.check_all()
    required = {
        "postgres": bool(providers.get("postgres")),
        "qdrant": bool(providers.get("qdrant")),
    }
    ready = all(required.values())
    if not ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"ready": False, "required": required, "providers": providers},
        )
    return {
        "ready": True,
        "required": required,
        "providers": providers,
        "timestamp": datetime.now(UTC).isoformat(),
    }
