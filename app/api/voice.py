from fastapi import APIRouter, HTTPException, status

from app.schemas.voice import VoiceModeUpdate, VoiceStateResponse, WakePhraseUpdate
from app.services.voice_service import VoiceService


router = APIRouter(prefix="/voice", tags=["voice"])
service = VoiceService()


@router.get("/state", response_model=VoiceStateResponse)
def get_voice_state() -> VoiceStateResponse:
    return VoiceStateResponse(**service.get_state().to_dict())


@router.patch("/mode", response_model=VoiceStateResponse)
def update_voice_mode(payload: VoiceModeUpdate) -> VoiceStateResponse:
    state = service.set_mode(payload.mode)
    return VoiceStateResponse(**state.to_dict())


@router.patch("/wake-phrase", response_model=VoiceStateResponse)
def update_wake_phrase(payload: WakePhraseUpdate) -> VoiceStateResponse:
    try:
        state = service.set_wake_phrase(payload.wake_phrase)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return VoiceStateResponse(**state.to_dict())
