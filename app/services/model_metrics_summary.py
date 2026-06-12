from __future__ import annotations

import json
from pathlib import Path


class ModelMetricsSummaryService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("logs/model_metrics.jsonl")

    def summary(self) -> dict[str, object]:
        if not self.path.exists():
            return {
                "executions_total": 0,
                "success_total": 0,
                "failure_total": 0,
                "fallback_total": 0,
                "average_latency_ms": 0.0,
                "providers": {},
            }

        records: list[dict[str, object]] = []
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                stripped = line.strip()
                if stripped:
                    records.append(json.loads(stripped))

        providers: dict[str, dict[str, int]] = {}
        latency_values: list[float] = []
        success_total = 0
        fallback_total = 0

        for record in records:
            provider = str(record.get("provider", "UNKNOWN"))
            success = bool(record.get("success", False))
            fallback_used = bool(record.get("fallback_used", False))
            latency = float(record.get("latency_ms", 0.0) or 0.0)

            provider_summary = providers.setdefault(provider, {"executions": 0, "successes": 0})
            provider_summary["executions"] += 1
            if success:
                provider_summary["successes"] += 1
                success_total += 1
            if fallback_used:
                fallback_total += 1
            latency_values.append(latency)

        total = len(records)
        average_latency = sum(latency_values) / total if total else 0.0
        return {
            "executions_total": total,
            "success_total": success_total,
            "failure_total": total - success_total,
            "fallback_total": fallback_total,
            "average_latency_ms": round(average_latency, 2),
            "providers": providers,
        }
