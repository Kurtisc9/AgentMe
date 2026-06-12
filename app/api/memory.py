from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.config import get_settings
from app.schemas.memory import (
    MemoryCreate,
    MemoryDecayResponse,
    MemoryListResponse,
    MemoryProjectSummaryResponse,
    MemoryResponse,
    MemoryUpdate,
)
from app.services.embedding_factory import build_embedding_provider
from app.services.embedding_service import EmbeddingService
from app.services.memory_manager import MemoryManager
from app.services.memory_service import MemoryService
from app.services.semantic_memory import SemanticMemoryService
from app.services.vector_memory import VectorMemoryStore


router = APIRouter(prefix="/memory", tags=["memory"])
settings = get_settings()
service = MemoryService()
primary_embedder = build_embedding_provider(settings)
manager = MemoryManager(
    local_store=service,
    primary_embedder=primary_embedder,
    fallback_embedder=EmbeddingService(),
)
semantic_service = SemanticMemoryService(
    VectorMemoryStore(
        settings.qdrant_url,
        embedding_service=primary_embedder,
    )
)


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(payload: MemoryCreate) -> MemoryResponse:
    try:
        record = service.create(
            memory_type=payload.memory_type,
            content=payload.content,
            tags=payload.tags,
            project=payload.project,
            importance=payload.importance,
        )
        provider = "local"
        try:
            semantic_service.initialize()
            semantic_service.upsert(record)
            provider = settings.embedding_provider
        except Exception:
            pass
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MemoryResponse(**asdict(record), embedding_provider=provider)


@router.get("", response_model=MemoryListResponse)
def list_memories(project: str | None = Query(default=None, max_length=120)) -> MemoryListResponse:
    return MemoryListResponse(memories=service.list_all(project=project))


@router.get("/search", response_model=MemoryListResponse)
def search_memories(
    query: str = Query(min_length=1, max_length=200),
    project: str | None = Query(default=None, max_length=120),
) -> MemoryListResponse:
    return MemoryListResponse(memories=service.search(query, project=project))


@router.get("/project/{project}", response_model=MemoryProjectSummaryResponse)
def summarize_project_memory(project: str) -> MemoryProjectSummaryResponse:
    return MemoryProjectSummaryResponse(**service.summarize_project(project))


@router.post("/decay", response_model=MemoryDecayResponse)
def decay_memories() -> MemoryDecayResponse:
    return MemoryDecayResponse(changed=service.decay_low_value_memories())


@router.get("/semantic-search", response_model=MemoryListResponse)
def semantic_search_memories(
    query: str = Query(min_length=1, max_length=200),
    limit: int = Query(default=5, ge=1, le=25),
) -> MemoryListResponse:
    try:
        semantic_service.initialize()
        results = semantic_service.search(query, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Semantic memory provider is unavailable.",
        ) from exc
    return MemoryListResponse(memories=results)


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(memory_id: str) -> MemoryResponse:
    try:
        record = service.get(memory_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return MemoryResponse(**record)


@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(memory_id: str, payload: MemoryUpdate) -> MemoryResponse:
    try:
        record = service.update(
            memory_id=memory_id,
            content=payload.content,
            tags=payload.tags,
            project=payload.project,
            importance=payload.importance,
        )
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return MemoryResponse(**record)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(memory_id: str) -> Response:
    try:
        service.delete(memory_id)
    except KeyError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
