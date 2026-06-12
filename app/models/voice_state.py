from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum


class VoiceMode(StrEnum):
    OFF = "OFF"
    PUSH_TO_TALK = "PUSH_TO_TALK"
    ALWAYS_LISTENING = "ALWAYS_LISTENING"


@dataclass(slots=True)
class VoiceState:
    mode: VoiceMode = VoiceMode.OFF
    wake_phrase: str = "Sage"
    microphone_enabled: bool = False
    speaking: bool = False
    updated_at: str = ""

    def touch(self) -> None:
        self.updated_at = datetime.now(UTC).isoformat()

    def to_dict(self) -> dict[str, object]:
        return asdict(self)
