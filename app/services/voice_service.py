from __future__ import annotations

from app.models.voice_state import VoiceMode, VoiceState


class VoiceService:
    def __init__(self, state: VoiceState | None = None) -> None:
        self.state = state or VoiceState()
        self.state.touch()

    def get_state(self) -> VoiceState:
        return self.state

    def set_mode(self, mode: VoiceMode) -> VoiceState:
        self.state.mode = mode
        self.state.microphone_enabled = mode != VoiceMode.OFF
        self.state.touch()
        return self.state

    def set_wake_phrase(self, wake_phrase: str) -> VoiceState:
        normalized = wake_phrase.strip()
        if not normalized:
            raise ValueError("Wake phrase cannot be empty.")
        self.state.wake_phrase = normalized
        self.state.touch()
        return self.state

    def set_speaking(self, speaking: bool) -> VoiceState:
        self.state.speaking = speaking
        self.state.touch()
        return self.state
