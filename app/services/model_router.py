from __future__ import annotations

from app.models.model_profile import ModelProfile
from app.services.model_registry import ModelRegistry


class ModelRouter:
    def __init__(self, registry: ModelRegistry | None = None) -> None:
        self.registry = registry or ModelRegistry()

    def select(self, task_type: str) -> ModelProfile:
        normalized = task_type.strip().lower() or "general"
        candidates = [
            model
            for model in self.registry.enabled_models()
            if normalized in {capability.lower() for capability in model.capabilities}
        ]
        if not candidates:
            candidates = [
                model
                for model in self.registry.enabled_models()
                if "general" in {capability.lower() for capability in model.capabilities}
            ]
        if not candidates:
            raise RuntimeError("No enabled model is available.")
        return sorted(candidates, key=lambda model: model.priority)[0]
