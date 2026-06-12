from pathlib import Path

from app.models.model_profile import ModelProfile, ModelProvider
from app.services.model_execution import ModelExecutionService
from app.services.model_metrics import ModelMetricsService
from app.services.model_registry import ModelRegistry
from app.services.model_router import ModelRouter


def test_code_task_selects_coder_model() -> None:
    selected = ModelRouter().select("code")

    assert selected.model_id == "qwen2.5-coder:7b"
    assert selected.provider == ModelProvider.OLLAMA


def test_unknown_task_falls_back_to_general_model() -> None:
    selected = ModelRouter().select("unknown-capability")

    assert "general" in selected.capabilities


class FailingOllama:
    def generate(self, *, model: str, prompt: str) -> str:
        raise RuntimeError("offline")


class WorkingLMStudio:
    def generate(self, *, model: str, prompt: str) -> str:
        return "fallback response"


def test_execution_falls_back_to_second_provider(tmp_path: Path) -> None:
    registry = ModelRegistry(
        models=(
            ModelProfile(
                name="Primary",
                provider=ModelProvider.OLLAMA,
                model_id="primary",
                capabilities=("general",),
                priority=1,
            ),
            ModelProfile(
                name="Fallback",
                provider=ModelProvider.LM_STUDIO,
                model_id="fallback",
                capabilities=("general",),
                priority=2,
            ),
        )
    )
    service = ModelExecutionService(
        registry=registry,
        router=ModelRouter(registry),
        ollama=FailingOllama(),
        lm_studio=WorkingLMStudio(),
        metrics=ModelMetricsService(tmp_path / "metrics.jsonl"),
        retries=0,
    )

    model, output, fallback_used = service.generate(
        task_type="general",
        prompt="Test prompt",
    )

    assert model.name == "Fallback"
    assert output == "fallback response"
    assert fallback_used is True
