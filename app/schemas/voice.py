from pydantic import BaseModel, Field

from app.models.voice_state import VoiceMode


class VoiceModeUpdate(BaseModel):
    mode: VoiceMode


class WakePhraseUpdate(BaseModel):
    wake_phrase: str = Field(min_length=1, max_length=50)


class VoiceStateResponse(BaseModel):
    mode: VoiceMode
    wake_phrase: str
    microphone_enabled: bool
    speaking: bool
    updated_at: str
