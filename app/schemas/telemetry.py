from pydantic import BaseModel


class SystemTelemetryResponse(BaseModel):
    timestamp: str
    hostname: str
    platform: str
    python_version: str
    cpu_count: int
    memory_total_bytes: int | None
    memory_available_bytes: int | None
    disk_total_bytes: int
    disk_free_bytes: int
    process_id: int


class MissionControlSummaryResponse(BaseModel):
    tasks_total: int
    approvals_total: int
    approvals_pending: int
    memories_total: int
    voice_events_total: int
    audit_log_exists: bool
    model_metrics_exists: bool
