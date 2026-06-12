from __future__ import annotations

from pathlib import Path


class MicrophoneService:
    """Microphone capture abstraction.

    Real device capture is intentionally isolated here so platform-specific
    code can be added without changing the voice API.
    """

    def capture(self, output_path: str | Path, duration_seconds: float = 5.0) -> Path:
        if duration_seconds <= 0 or duration_seconds > 60:
            raise ValueError("Capture duration must be between 0 and 60 seconds.")
        raise RuntimeError("Microphone capture provider is not configured.")
