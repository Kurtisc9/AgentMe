import json
from pathlib import Path

from app.services.model_metrics_summary import ModelMetricsSummaryService
from app.services.system_telemetry import SystemTelemetryService


def test_system_telemetry_collects_core_fields() -> None:
    snapshot = SystemTelemetryService().collect()

    assert snapshot.cpu_count >= 1
    assert snapshot.disk_total_bytes >= snapshot.disk_free_bytes
    assert snapshot.process_id > 0
    assert snapshot.timestamp


def test_model_metrics_summary_handles_missing_file(tmp_path: Path) -> None:
    summary = ModelMetricsSummaryService(tmp_path / "missing.jsonl").summary()

    assert summary["executions_total"] == 0
    assert summary["average_latency_ms"] == 0.0


def test_model_metrics_summary_aggregates_records(tmp_path: Path) -> None:
    path = tmp_path / "metrics.jsonl"
    records = [
        {
            "provider": "OLLAMA",
            "success": True,
            "fallback_used": False,
            "latency_ms": 100.0,
        },
        {
            "provider": "LM_STUDIO",
            "success": False,
            "fallback_used": True,
            "latency_ms": 300.0,
        },
    ]
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")

    summary = ModelMetricsSummaryService(path).summary()

    assert summary["executions_total"] == 2
    assert summary["success_total"] == 1
    assert summary["failure_total"] == 1
    assert summary["fallback_total"] == 1
    assert summary["average_latency_ms"] == 200.0
