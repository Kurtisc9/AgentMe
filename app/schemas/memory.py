from pydantic import BaseModel, Field

from app.models.memory_record import MemoryType


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str = Field(min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list)


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=4000)
    tags: list[str] | None = None


class MemoryResponse(BaseModel):
    memory_id: str
    memory_type: MemoryType
    content: str
    tags: list[str]
    created_at: str
    embedding_provider: str | None = None


class MemoryListResponse(BaseModel):
    memories: list[dict[str, object]]
