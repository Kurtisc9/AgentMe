from fastapi import APIRouter, HTTPException, status

from app.config import get_settings
from app.models.model_profile import ModelProvider
from app.schemas.models import (
    ModelGenerateRequest,
    ModelGenerateResponse,
    ModelListResponse,
    ModelProfileResponse,
    ModelRouteRequest,
)
from app.services.lmstudio_chat import LMStudioChatService
from app.services.model_registry import ModelRegistry
from app.services.model_router import ModelRouter
from app.services.ollama_chat import OllamaChatService


router = APIRouter(prefix="/models", tags=["models"])
settings = get_settings()
registry = ModelRegistry()
model_router = ModelRouter(registry)
ollama = OllamaChatService(settings.ollama_base_url)
lm_studio = LMStudioChatService(settings.lm_studio_base_url)


@router.get("", response_model=ModelListResponse)
def list_models() -> ModelListResponse:
    return ModelListResponse(
        models=[ModelProfileResponse(**item) for item in registry.list_models()]
    )


@router.post("/route", response_model=ModelProfileResponse)
def route_model(payload: ModelRouteRequest) -> ModelProfileResponse:
    try:
        selected = model_router.select(payload.task_type)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return ModelProfileResponse(**selected.to_dict())


@router.post("/generate", response_model=ModelGenerateResponse)
def generate(payload: ModelGenerateRequest) -> ModelGenerateResponse:
    try:
        selected = model_router.select(payload.task_type)
        if selected.provider == ModelProvider.OLLAMA:
            output = ollama.generate(model=selected.model_id, prompt=payload.prompt)
        else:
            output = lm_studio.generate(model=selected.model_id, prompt=payload.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Selected model provider is unavailable.",
        ) from exc

    return ModelGenerateResponse(
        model_name=selected.name,
        provider=selected.provider.value,
        model_id=selected.model_id,
        output=output,
    )
