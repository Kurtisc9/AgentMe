from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.desktop import (
    DesktopExecuteRequest,
    DesktopExecuteResponse,
    DesktopProfileListResponse,
    DesktopProfilePayload,
    DesktopProfileResponse,
)
from app.services.desktop_control_service import DesktopControlService
from app.services.desktop_profile_service import DesktopProfile


router = APIRouter(prefix="/desktop", tags=["desktop"])
service = DesktopControlService()


@router.get("/profiles", response_model=DesktopProfileListResponse)
def list_desktop_profiles(device: str | None = Query(default=None, pattern="^(PC1|PC2)$")) -> DesktopProfileListResponse:
    return DesktopProfileListResponse(profiles=service.list_profiles(device=device))


@router.put("/profiles/{profile_id}", response_model=DesktopProfileResponse)
def upsert_desktop_profile(profile_id: str, payload: DesktopProfilePayload) -> DesktopProfileResponse:
    if profile_id != payload.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile ID mismatch.")
    profile = service.profiles.create_or_update(DesktopProfile(**payload.model_dump()))
    return DesktopProfileResponse(**profile.to_dict())


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_desktop_profile(profile_id: str) -> Response:
    try:
        service.profiles.delete(profile_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
