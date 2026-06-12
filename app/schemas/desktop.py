from pydantic import BaseModel, Field


class DesktopProfileResponse(BaseModel):
    id: str
    name: str
    type: str
    risk_level: str
    command: str
    arguments: list[str]


class DesktopProfileListResponse(BaseModel):
    profiles: list[DesktopProfileResponse]


class DesktopExecuteRequest(BaseModel):
    profile_id: str = Field(min_length=1, max_length=100)
    approval_id: str | None = Field(default=None, min_length=1, max_length=200)


class DesktopExecuteResponse(BaseModel):
    profile_id: str
    profile_name: str
    profile_type: str
    risk_level: str
    success: bool
    output: str
