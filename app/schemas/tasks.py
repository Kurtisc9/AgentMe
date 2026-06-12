from pydantic import BaseModel, Field

from app.core.commander import RiskLevel


class TaskCreate(BaseModel):
    description: str = Field(min_length=3, max_length=2000)


class TaskRouteResponse(BaseModel):
    description: str
    assigned_agent: str
    risk_level: RiskLevel
    approval_required: bool
    blocked: bool
    reason: str
