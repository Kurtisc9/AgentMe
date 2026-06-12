from fastapi import FastAPI

from app.api.agents import router as agents_router
from app.api.approvals import router as approvals_router
from app.api.audit import router as audit_router
from app.api.health import router as health_router
from app.api.memory import router as memory_router
from app.api.models import router as models_router
from app.api.providers import router as providers_router
from app.api.tasks import router as tasks_router
from app.api.voice import router as voice_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(approvals_router)
app.include_router(audit_router)
app.include_router(memory_router)
app.include_router(providers_router)
app.include_router(voice_router)
app.include_router(agents_router)
app.include_router(models_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "message": "Sage foundation is running.",
    }
