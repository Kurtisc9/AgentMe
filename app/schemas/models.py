from pydantic import BaseModel, Field


class ModelRouteRequest(BaseModel):
    task_type: str = Field(min_length=1, max_length=100)


class ModelGenerateRequest(BaseModel):
    task_type: str = Field(default="general", min_length=1, max_length=100)
    prompt: str = Field(min_length=1, max_length=8000)


class ModelProfileResponse(BaseModel):
    name: str
    provider: str
    model_id: str
    capabilities: list[str]
    priority: int
    enabled: bool


class ModelListResponse(BaseModel):
    models: list[ModelProfileResponse]


class ModelGenerateResponse(BaseModel):
    model_name: str
    provider: str
    model_id: str
    output: str
