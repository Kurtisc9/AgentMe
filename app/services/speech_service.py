from __future__ import annotations

import subprocess
from pathlib import Path


class SpeechService:
    """Piper text-to-speech adapter foundation."""

    def __init__(self, voice_path: str | Path) -> None:
        self.voice_path = Path(voice_path)

    def synthesize(self, text: str, output_path: str | Path) -> Path:
        normalized = text.strip()
        if not normalized:
            raise ValueError("Speech text cannot be empty.")
        if not self.voice_path.exists():
            raise FileNotFoundError(f"Piper voice not found: {self.voice_path}")

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "piper",
            "--model",
            str(self.voice_path),
            "--output_file",
            str(output),
        ]
        subprocess.run(
            command,
            input=normalized,
            text=True,
            check=True,
            capture_output=True,
        )
        return output
