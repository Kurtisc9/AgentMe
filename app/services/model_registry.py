from __future__ import annotations

from app.models.model_profile import ModelProfile, ModelProvider


DEFAULT_MODELS: tuple[ModelProfile, ...] = (
    ModelProfile(
        name="Sage General",
        provider=ModelProvider.OLLAMA,
        model_id="llama3.1:8b",
        capabilities=("general", "writing", "planning"),
        priority=10,
    ),
    ModelProfile(
        name="Code Local",
        provider=ModelProvider.OLLAMA,
        model_id="qwen2.5-coder:7b",
        capabilities=("code", "debug", "test"),
        priority=5,
    ),
    ModelProfile(
        name="LM Studio Fallback",
        provider=ModelProvider.LM_STUDIO,
        model_id="local-model",
        capabilities=("general", "writing", "code", "analysis"),
        priority=50,
    ),
)


class ModelRegistry:
    def __init__(self, models: tuple[ModelProfile, ...] | None = None) -> None:
        self.models = models or DEFAULT_MODELS

    def list_models(self) -> list[dict[str, object]]:
        return [model.to_dict() for model in self.models]

    def enabled_models(self) -> list[ModelProfile]:
        return [model for model in self.models if model.enabled]
