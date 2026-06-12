from pathlib import Path

from app.models.voice_state import VoiceMode
from app.services.voice_service import VoiceService
from app.services.voice_loop import VoiceLoopService


def test_voice_mode_updates_microphone_state() -> None:
    service = VoiceService()

    state = service.set_mode(VoiceMode.PUSH_TO_TALK)

    assert state.mode == VoiceMode.PUSH_TO_TALK
    assert state.microphone_enabled is True


def test_voice_off_disables_microphone() -> None:
    service = VoiceService()
    service.set_mode(VoiceMode.ALWAYS_LISTENING)

    state = service.set_mode(VoiceMode.OFF)

    assert state.microphone_enabled is False


class FakeMicrophone:
    def capture(self, output_path: str | Path, duration_seconds: float = 5.0) -> Path:
        return Path(output_path)


class FakeTranscription:
    def transcribe(self, audio_path: str | Path) -> str:
        return "Sage, review this Python code"


class FakeTaskService:
    def __init__(self) -> None:
        self.received: str | None = None

    def route(self, description: str):
        self.received = description
        return {"description": description}


def test_voice_loop_routes_detected_command() -> None:
    task_service = FakeTaskService()
    loop = VoiceLoopService(
        microphone=FakeMicrophone(),
        transcription=FakeTranscription(),
        task_service=task_service,
    )

    result = loop.run_once()

    assert task_service.received == "review this Python code"
    assert result == {"description": "review this Python code"}
