from __future__ import annotations

from app.config import Settings
from app.services.embedding_service import EmbeddingService
from app.services.lmstudio_embedding import LMStudioEmbeddingService
from app.services.ollama_embedding import OllamaEmbeddingService


def build_embedding_provider(settings: Settings) -> object:
    provider = settings.embedding_provider.strip().lower()

    if provider == "ollama":
        return OllamaEmbeddingService(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )

    if provider in {"lmstudio", "lm_studio", "lm-studio"}:
        return LMStudioEmbeddingService(
            base_url=settings.lm_studio_base_url,
            model=settings.lm_studio_embedding_model,
        )

    return EmbeddingService()
