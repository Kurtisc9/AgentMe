from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.models.voice_history import VoiceEventType
from app.schemas.voice import (
    SpeakRequest,
    SpeechResponse,
    TranscriptionResponse,
    VoiceCommandRequest,
    VoiceCommandResponse,
    VoiceHistoryResponse,
    VoiceModeUpdate,
    VoiceStateResponse,
    WakePhraseUpdate,
)
from app.services.speech_service import SpeechService
from app.services.task_service import TaskService
from app.services.transcription_service import TranscriptionService
from app.services.voice_history_service import VoiceHistoryService
from app.services.voice_service import VoiceService


router = APIRouter(prefix="/voice", tags=["voice"])
service = VoiceService()
transcription_service = TranscriptionService()
speech_service = SpeechService("voices/en_US-lessac-medium.onnx")
task_service = TaskService()
history_service = VoiceHistoryService()


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


@router.post("/transcribe", response_model=TranscriptionResponse)
def transcribe_audio(file: UploadFile = File(...)) -> TranscriptionResponse:
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as temporary:
            temporary.write(file.file.read())
            temp_path = Path(temporary.name)
        text = transcription_service.transcribe(temp_path)
        history_service.append(event_type=VoiceEventType.TRANSCRIPTION, content=text)
        return TranscriptionResponse(text=text)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    finally:
        if "temp_path" in locals() and temp_path.exists():
            temp_path.unlink(missing_ok=True)


@router.post("/speak", response_model=SpeechResponse)
def speak_text(payload: SpeakRequest) -> SpeechResponse:
    output_path = Path("data/voice_output/sage_response.wav")
    try:
        service.set_speaking(True)
        created = speech_service.synthesize(payload.text, output_path)
        history_service.append(event_type=VoiceEventType.SPEECH, content=payload.text)
        return SpeechResponse(output_path=str(created))
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    finally:
        service.set_speaking(False)


@router.post("/command", response_model=VoiceCommandResponse)
def route_voice_command(payload: VoiceCommandRequest) -> VoiceCommandResponse:
    record = task_service.route(payload.text)
    history_service.append(
        event_type=VoiceEventType.COMMAND,
        content=payload.text,
        task_id=record.task_id,
    )
    return VoiceCommandResponse(
        task_id=record.task_id,
        assigned_agent=record.assigned_agent,
        risk_level=record.risk_level.value,
        approval_required=record.approval_required,
        blocked=record.blocked,
        status=record.status.value,
        reason=record.reason,
    )


@router.get("/history", response_model=VoiceHistoryResponse)
def get_voice_history() -> VoiceHistoryResponse:
    return VoiceHistoryResponse(events=history_service.list_all())
