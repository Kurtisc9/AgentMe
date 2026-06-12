from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.memory import MemoryCreate, MemoryListResponse, MemoryResponse
from app.services.memory_service import MemoryService


router = APIRouter(prefix="/memory", tags=["memory"])
service = MemoryService()


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(payload: MemoryCreate) -> MemoryResponse:
    try:
        record = service.create(
            memory_type=payload.memory_type,
            content=payload.content,
            tags=payload.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MemoryResponse(**asdict(record))


@router.get("", response_model=MemoryListResponse)
def list_memories() -> MemoryListResponse:
    return MemoryListResponse(memories=service.list_all())


@router.get("/search", response_model=MemoryListResponse)
def search_memories(query: str = Query(min_length=1, max_length=200)) -> MemoryListResponse:
    return MemoryListResponse(memories=service.search(query))
