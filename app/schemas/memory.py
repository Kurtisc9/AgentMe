from pydantic import BaseModel, Field

from app.models.memory_record import MemoryType


class MemoryCreate(BaseModel):
    memory_type: MemoryType
    content: str = Field(min_length=1, max_length=4000)
    tags: list[str] = Field(default_factory=list)
    project: str | None = Field(default=None, max_length=120)
    importance: int = Field(default=3, ge=1, le=5)


class MemoryUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=4000)
    tags: list[str] | None = None
    project: str | None = Field(default=None, max_length=120)
    importance: int | None = Field(default=None, ge=1, le=5)


class MemoryResponse(BaseModel):
    memory_id: str
    memory_type: MemoryType
    content: str
    tags: list[str]
    created_at: str
    project: str | None = None
    importance: int = 3
    access_count: int = 0
    last_accessed_at: str | None = None
    summary: str | None = None
    embedding_provider: str | None = None


class MemoryListResponse(BaseModel):
    memories: list[dict[str, object]]


class MemoryProjectSummaryResponse(BaseModel):
    project: str
    memory_count: int
    summary: str
    top_memories: list[dict[str, object]]


class MemoryDecayResponse(BaseModel):
    changed: int
