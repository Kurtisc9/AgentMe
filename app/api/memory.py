from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.schemas.memory import MemoryCreate, MemoryListResponse, MemoryResponse, MemoryUpdate
from app.services.memory_manager import MemoryManager
from app.services.memory_service import MemoryService


router = APIRouter(prefix="/memory", tags=["memory"])
service = MemoryService()
manager = MemoryManager(local_store=service)


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(payload: MemoryCreate) -> MemoryResponse:
    try:
        record, provider = manager.create(
            memory_type=payload.memory_type,
            content=payload.content,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MemoryResponse(**asdict(record), embedding_provider=provider)


@router.get("", response_model=MemoryListResponse)
def list_memories() -> MemoryListResponse:
    return MemoryListResponse(memories=service.list_all())


@router.get("/search", response_model=MemoryListResponse)
def search_memories(query: str = Query(min_length=1, max_length=200)) -> MemoryListResponse:
    return MemoryListResponse(memories=service.search(query))


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
