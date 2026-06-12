from fastapi import APIRouter, HTTPException, status

from app.schemas.agents import (
    AgentExecuteRequest,
    AgentExecutionResponse,
    AgentListResponse,
)
from app.services.agent_service import AgentService


router = APIRouter(prefix="/agents", tags=["agents"])
service = AgentService()


@router.get("", response_model=AgentListResponse)
def list_agents() -> AgentListResponse:
    return AgentListResponse(agents=service.list_agents())


@router.post("/{agent_name}/execute", response_model=AgentExecutionResponse)
def execute_agent(agent_name: str, payload: AgentExecuteRequest) -> AgentExecutionResponse:
    try:
        result = service.execute(agent_name=agent_name, task=payload.task)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AgentExecutionResponse(**result.to_dict())
