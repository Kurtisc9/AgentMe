from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path


class ModelMetricsService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("logs/model_metrics.jsonl")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(
        self,
        *,
        model_name: str,
        provider: str,
        model_id: str,
        success: bool,
        latency_ms: float,
        fallback_used: bool,
        error: str | None = None,
    ) -> None:
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "model_name": model_name,
            "provider": provider,
            "model_id": model_id,
            "success": success,
            "latency_ms": latency_ms,
            "fallback_used": fallback_used,
            "error": error,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")
