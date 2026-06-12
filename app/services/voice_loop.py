from __future__ import annotations

from pathlib import Path

from app.services.task_service import TaskService
from app.services.transcription_service import TranscriptionService
from app.services.wake_phrase_service import WakePhraseService
from app.services.windows_microphone import WindowsMicrophoneService


class VoiceLoopService:
    def __init__(
        self,
        *,
        microphone: WindowsMicrophoneService | None = None,
        transcription: TranscriptionService | None = None,
        task_service: TaskService | None = None,
        wake_phrase: str = "Sage",
    ) -> None:
        self.microphone = microphone or WindowsMicrophoneService()
        self.transcription = transcription or TranscriptionService()
        self.task_service = task_service or TaskService()
        self.detector = WakePhraseService(wake_phrase)

    def run_once(
        self,
        *,
        output_path: str | Path = "data/voice_input/latest.wav",
        duration_seconds: float = 5.0,
    ):
        audio_path = self.microphone.capture(output_path, duration_seconds)
        transcript = self.transcription.transcribe(audio_path)
        command = self.detector.strip_wake_phrase(transcript)
        if command is None or not command.strip():
            return None
        return self.task_service.route(command)
