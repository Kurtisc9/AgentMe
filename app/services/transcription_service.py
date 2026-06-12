from __future__ import annotations

from pathlib import Path


class TranscriptionService:
    """Faster-Whisper adapter foundation.

    The model is loaded lazily so the API can start even when voice dependencies
    are not installed yet.
    """

    def __init__(self, model_name: str = "small") -> None:
        self.model_name = model_name
        self._model = None

    def transcribe(self, audio_path: str | Path) -> str:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        model = self._get_model()
        segments, _ = model.transcribe(str(path))
        text = " ".join(segment.text.strip() for segment in segments).strip()
        if not text:
            raise RuntimeError("No speech was detected.")
        return text

    def _get_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError("faster-whisper is not installed.") from exc
            self._model = WhisperModel(self.model_name)
        return self._model
