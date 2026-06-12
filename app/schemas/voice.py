from pydantic import BaseModel, Field

from app.models.voice_state import VoiceMode


class VoiceModeUpdate(BaseModel):
    mode: VoiceMode


class WakePhraseUpdate(BaseModel):
    wake_phrase: str = Field(min_length=1, max_length=50)


class SpeakRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class VoiceCommandRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)


class VoiceStateResponse(BaseModel):
    mode: VoiceMode
    wake_phrase: str
    microphone_enabled: bool
    speaking: bool
    updated_at: str


class TranscriptionResponse(BaseModel):
    text: str


class SpeechResponse(BaseModel):
    output_path: str


class VoiceCommandResponse(BaseModel):
    task_id: str
    assigned_agent: str
    risk_level: str
    approval_required: bool
    blocked: bool
    status: str
    reason: str


class VoiceHistoryResponse(BaseModel):
    events: list[dict[str, object]]
