from pydantic import BaseModel, Field


class AutomationExecuteRequest(BaseModel):
    integration_name: str = Field(min_length=1, max_length=100)
    action: str = Field(min_length=1, max_length=100)
    payload: dict[str, object] = Field(default_factory=dict)
    approved: bool = False


class IntegrationSummary(BaseModel):
    name: str
    description: str
    actions: list[str]


class IntegrationListResponse(BaseModel):
    integrations: list[IntegrationSummary]


class AutomationExecutionResponse(BaseModel):
    integration_name: str
    action: str
    success: bool
    output: str
