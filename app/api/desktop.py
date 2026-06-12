from fastapi import APIRouter, HTTPException, status

from app.schemas.desktop import (
    DesktopExecuteRequest,
    DesktopExecuteResponse,
    DesktopProfileListResponse,
)
from app.services.desktop_control_service import DesktopControlService


router = APIRouter(prefix="/desktop", tags=["desktop"])
service = DesktopControlService()


@router.get("/profiles", response_model=DesktopProfileListResponse)
def list_desktop_profiles() -> DesktopProfileListResponse:
    return DesktopProfileListResponse(profiles=service.list_profiles())


@router.post("/execute", response_model=DesktopExecuteResponse)
def execute_desktop_profile(payload: DesktopExecuteRequest) -> DesktopExecuteResponse:
    try:
        result = service.execute(
            profile_id=payload.profile_id,
            approval_id=payload.approval_id,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return DesktopExecuteResponse(**result)
