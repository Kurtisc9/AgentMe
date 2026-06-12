from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.models.voice_history import VoiceEventType
from app.services.voice_desktop_service import VoiceDesktopService
from app.services.voice_history_service import VoiceHistoryService


class VoiceDesktopRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    approval_id: str | None = Field(default=None, min_length=1, max_length=200)


class VoiceDesktopResponse(BaseModel):
    matched: bool
    profile_id: str | None
    result: dict[str, object] | None
    reason: str


router = APIRouter(prefix="/voice-desktop", tags=["voice-desktop"])
voice_desktop = VoiceDesktopService()
history = VoiceHistoryService()


@router.post("/route", response_model=VoiceDesktopResponse)
def route_voice_desktop(payload: VoiceDesktopRequest) -> VoiceDesktopResponse:
    try:
        result = voice_desktop.route(text=payload.text, approval_id=payload.approval_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    history.append(
        event_type=VoiceEventType.COMMAND,
        content=f"desktop:{payload.text}",
        task_id=str(result.get("profile_id")) if result.get("profile_id") else None,
    )
    return VoiceDesktopResponse(**result)
