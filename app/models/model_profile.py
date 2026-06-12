from dataclasses import asdict, dataclass
from enum import StrEnum


class ModelProvider(StrEnum):
    OLLAMA = "OLLAMA"
    LM_STUDIO = "LM_STUDIO"


@dataclass(slots=True)
class ModelProfile:
    name: str
    provider: ModelProvider
    model_id: str
    capabilities: tuple[str, ...]
    priority: int = 100
    enabled: bool = True

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["provider"] = self.provider.value
        data["capabilities"] = list(self.capabilities)
        return data
