from pydantic import BaseModel, Field


class OrchestrationRunRequest(BaseModel):
    objective: str = Field(min_length=1, max_length=4000)


class OrchestrationStepResponse(BaseModel):
    step_id: str
    agent_name: str
    task: str
    success: bool
    output: str


class OrchestrationRunResponse(BaseModel):
    run_id: str
    objective: str
    status: str
    steps: list[OrchestrationStepResponse]
    created_at: str


class OrchestrationListResponse(BaseModel):
    runs: list[OrchestrationRunResponse]
