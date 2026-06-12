from __future__ import annotations

from pathlib import Path


class WindowsMicrophoneService:
    """Windows microphone capture using sounddevice and scipy."""

    def __init__(self, sample_rate: int = 16000, channels: int = 1) -> None:
        self.sample_rate = sample_rate
        self.channels = channels

    def capture(self, output_path: str | Path, duration_seconds: float = 5.0) -> Path:
        if duration_seconds <= 0 or duration_seconds > 60:
            raise ValueError("Capture duration must be between 0 and 60 seconds.")

        try:
            import sounddevice as sd
            from scipy.io.wavfile import write
        except ImportError as exc:
            raise RuntimeError("sounddevice and scipy are required for microphone capture.") from exc

        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        frames = int(duration_seconds * self.sample_rate)
        recording = sd.rec(
            frames,
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
        )
        sd.wait()
        write(str(output), self.sample_rate, recording)
        return output
