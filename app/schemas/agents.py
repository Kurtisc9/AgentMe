from pydantic import BaseModel, Field


class AgentExecuteRequest(BaseModel):
    task: str = Field(min_length=1, max_length=4000)


class AgentResponse(BaseModel):
    name: str
    description: str
    capabilities: list[str]


class AgentListResponse(BaseModel):
    agents: list[AgentResponse]


class AgentExecutionResponse(BaseModel):
    agent_name: str
    task: str
    output: str
    success: bool
