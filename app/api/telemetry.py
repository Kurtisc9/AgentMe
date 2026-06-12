from fastapi import APIRouter

from app.schemas.telemetry import (
    MissionControlSummaryResponse,
    SystemTelemetryResponse,
)
from app.services.mission_control import MissionControlService
from app.services.model_metrics_summary import ModelMetricsSummaryService
from app.services.system_telemetry import SystemTelemetryService


router = APIRouter(prefix="/telemetry", tags=["telemetry"])
system_service = SystemTelemetryService()
mission_control = MissionControlService()
model_metrics = ModelMetricsSummaryService()


@router.get("/system", response_model=SystemTelemetryResponse)
def get_system_telemetry() -> SystemTelemetryResponse:
    return SystemTelemetryResponse(**system_service.collect().to_dict())


@router.get("/summary", response_model=MissionControlSummaryResponse)
def get_mission_control_summary() -> MissionControlSummaryResponse:
    return MissionControlSummaryResponse(**mission_control.summary())


@router.get("/models")
def get_model_metrics_summary() -> dict[str, object]:
    return model_metrics.summary()
