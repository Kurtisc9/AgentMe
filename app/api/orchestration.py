from fastapi import APIRouter

from app.schemas.orchestration import (
    OrchestrationListResponse,
    OrchestrationRunRequest,
    OrchestrationRunResponse,
)
from app.services.orchestration_service import OrchestrationService


router = APIRouter(prefix="/orchestration", tags=["orchestration"])
service = OrchestrationService()


@router.get("", response_model=OrchestrationListResponse)
def list_orchestrations() -> OrchestrationListResponse:
    return OrchestrationListResponse(runs=service.list_runs())


@router.post("/run", response_model=OrchestrationRunResponse)
def run_orchestration(payload: OrchestrationRunRequest) -> OrchestrationRunResponse:
    result = service.run(payload.objective)
    return OrchestrationRunResponse(**result)
