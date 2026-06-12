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
    VoiceConfirmRequest,
    VoiceConfirmationResponse,
    VoiceHistoryResponse,
    VoiceModeUpdate,
    VoiceStateResponse,
    WakePhraseResponse,
    WakePhraseUpdate,
)
from app.services.approval_service import ApprovalService
from app.services.speech_service import SpeechService
from app.services.task_service import TaskService
from app.services.transcription_service import TranscriptionService
from app.services.voice_history_service import VoiceHistoryService
from app.services.voice_service import VoiceService
from app.services.wake_phrase_service import WakePhraseService


router = APIRouter(prefix="/voice", tags=["voice"])
service = VoiceService()
transcription_service = TranscriptionService()
speech_service = SpeechService("voices/en_US-lessac-medium.onnx")
task_service = TaskService()
approval_service = ApprovalService()
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


@router.post("/wake-detect", response_model=WakePhraseResponse)
def detect_wake_phrase(payload: VoiceCommandRequest) -> WakePhraseResponse:
    detector = WakePhraseService(service.get_state().wake_phrase)
    command = detector.strip_wake_phrase(payload.text)
    return WakePhraseResponse(detected=command is not None, command=command)


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


@router.post("/confirm", response_model=VoiceConfirmationResponse)
def confirm_voice_approval(payload: VoiceConfirmRequest) -> VoiceConfirmationResponse:
    expected = "approve" if payload.approve else "deny"
    normalized = payload.confirmation_phrase.strip().lower()
    if normalized not in {expected, f"sage {expected}", f"yes {expected}"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Say '{expected}' to confirm this decision.",
        )

    try:
        result = approval_service.decide(
            approval_id=payload.approval_id,
            approver_role="KurtisC",
            approve=payload.approve,
            note=payload.note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return VoiceConfirmationResponse(
        approval_id=str(result["approval_id"]),
        status=str(result["status"]),
        decision_note=result.get("decision_note"),
    )


@router.get("/history", response_model=VoiceHistoryResponse)
def get_voice_history() -> VoiceHistoryResponse:
    return VoiceHistoryResponse(events=history_service.list_all())
