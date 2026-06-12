from fastapi import APIRouter

from app.config import get_settings
from app.services.provider_health import ProviderHealthService


router = APIRouter(prefix="/providers", tags=["providers"])
settings = get_settings()
service = ProviderHealthService()


@router.get("/health")
def provider_health() -> dict[str, object]:
    return {
        "embedding_provider": settings.embedding_provider,
        "ollama": service.check_ollama(settings.ollama_base_url),
        "lm_studio": service.check_lm_studio(settings.lm_studio_base_url),
        "postgres": service.check_postgres(settings.postgres_url),
        "qdrant": service.check_qdrant(settings.qdrant_url),
    }
