from dataclasses import asdict

from fastapi import APIRouter, HTTPException, status

from app.schemas.tasks import TaskCreate, TaskRouteResponse
from app.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["tasks"])
service = TaskService()


@router.post("/route", response_model=TaskRouteResponse)
def route_task(payload: TaskCreate) -> TaskRouteResponse:
    try:
        result = service.route(payload.description)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return TaskRouteResponse(**asdict(result))
