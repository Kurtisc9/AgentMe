from __future__ import annotations

from time import perf_counter, sleep

from app.models.model_profile import ModelProfile, ModelProvider
from app.services.lmstudio_chat import LMStudioChatService
from app.services.model_metrics import ModelMetricsService
from app.services.model_registry import ModelRegistry
from app.services.model_router import ModelRouter
from app.services.ollama_chat import OllamaChatService


class ModelExecutionService:
    def __init__(
        self,
        *,
        registry: ModelRegistry | None = None,
        router: ModelRouter | None = None,
        ollama: OllamaChatService | None = None,
        lm_studio: LMStudioChatService | None = None,
        metrics: ModelMetricsService | None = None,
        retries: int = 1,
    ) -> None:
        self.registry = registry or ModelRegistry()
        self.router = router or ModelRouter(self.registry)
        self.ollama = ollama or OllamaChatService()
        self.lm_studio = lm_studio or LMStudioChatService()
        self.metrics = metrics or ModelMetricsService()
        self.retries = retries

    def generate(self, *, task_type: str, prompt: str) -> tuple[ModelProfile, str, bool]:
        primary = self.router.select(task_type)
        candidates = [primary] + [
            model
            for model in self.registry.enabled_models()
            if model.name != primary.name
            and (
                task_type.lower() in {cap.lower() for cap in model.capabilities}
                or "general" in {cap.lower() for cap in model.capabilities}
            )
        ]

        last_error: Exception | None = None
        for index, model in enumerate(candidates):
            started = perf_counter()
            for attempt in range(self.retries + 1):
                try:
                    output = self._call(model, prompt)
                    self.metrics.record(
                        model_name=model.name,
                        provider=model.provider.value,
                        model_id=model.model_id,
                        success=True,
                        latency_ms=(perf_counter() - started) * 1000,
                        fallback_used=index > 0,
                    )
                    return model, output, index > 0
                except Exception as exc:
                    last_error = exc
                    if attempt < self.retries:
                        sleep(0.2)

            self.metrics.record(
                model_name=model.name,
                provider=model.provider.value,
                model_id=model.model_id,
                success=False,
                latency_ms=(perf_counter() - started) * 1000,
                fallback_used=index > 0,
                error=str(last_error),
            )

        raise RuntimeError("All configured model providers failed.") from last_error

    def _call(self, model: ModelProfile, prompt: str) -> str:
        if model.provider == ModelProvider.OLLAMA:
            return self.ollama.generate(model=model.model_id, prompt=prompt)
        return self.lm_studio.generate(model=model.model_id, prompt=prompt)
