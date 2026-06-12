from pydantic import BaseModel


class SystemTelemetryResponse(BaseModel):
    timestamp: str
    hostname: str
    platform: str
    python_version: str
    cpu_count: int
    cpu_percent: float | None
    memory_total_bytes: int | None
    memory_available_bytes: int | None
    memory_percent: float | None
    disk_total_bytes: int
    disk_free_bytes: int
    disk_percent: float
    process_id: int
    gpu_name: str | None
    gpu_utilization_percent: float | None
    gpu_memory_used_mb: float | None
    gpu_memory_total_mb: float | None


class MissionControlSummaryResponse(BaseModel):
    tasks_total: int
    approvals_total: int
    approvals_pending: int
    memories_total: int
    voice_events_total: int
    audit_log_exists: bool
    model_metrics_exists: bool
