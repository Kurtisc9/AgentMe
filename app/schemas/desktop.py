from pydantic import BaseModel, Field


class DesktopProfilePayload(BaseModel):
    id: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=100)
    type: str = Field(min_length=1, max_length=50)
    risk_level: str = Field(pattern="^(LOW|MEDIUM|HIGH)$")
    command: str = Field(min_length=1, max_length=2000)
    arguments: list[str] = Field(default_factory=list)
    device: str = Field(default="PC1", pattern="^(PC1|PC2)$")
    favorite: bool = False


class DesktopProfileResponse(DesktopProfilePayload):
    pass


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
