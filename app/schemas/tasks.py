from pydantic import BaseModel, Field

from app.core.commander import RiskLevel
from app.models.task_record import TaskStatus


class TaskCreate(BaseModel):
    description: str = Field(min_length=3, max_length=2000)


class TaskRouteResponse(BaseModel):
    task_id: str
    description: str
    assigned_agent: str
    risk_level: RiskLevel
    approval_required: bool
    blocked: bool
    reason: str
    status: TaskStatus
    created_at: str


class TaskListResponse(BaseModel):
    tasks: list[dict[str, object]]
