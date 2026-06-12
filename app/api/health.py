from datetime import UTC, datetime

from fastapi import APIRouter


router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, object]:
    return {
        "ok": True,
        "service": "AgentMe / Sage",
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
    }
