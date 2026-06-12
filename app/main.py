from fastapi import FastAPI

from app.api.approvals import router as approvals_router
from app.api.health import router as health_router
from app.api.tasks import router as tasks_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(tasks_router)
app.include_router(approvals_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "message": "Sage foundation is running.",
    }
