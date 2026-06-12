from fastapi import APIRouter, HTTPException, status

from app.schemas.automations import (
    AutomationExecuteRequest,
    AutomationExecutionResponse,
    IntegrationListResponse,
)
from app.services.automation_service import AutomationService


router = APIRouter(prefix="/automations", tags=["automations"])
service = AutomationService()


@router.get("", response_model=IntegrationListResponse)
def list_integrations() -> IntegrationListResponse:
    return IntegrationListResponse(integrations=service.list_integrations())


@router.post("/execute", response_model=AutomationExecutionResponse)
def execute_automation(payload: AutomationExecuteRequest) -> AutomationExecutionResponse:
    try:
        result = service.execute(
            integration_name=payload.integration_name,
            action=payload.action,
            payload=payload.payload,
            approval_id=payload.approval_id,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Automation provider is unavailable.",
        ) from exc

    return AutomationExecutionResponse(**result.to_dict())
