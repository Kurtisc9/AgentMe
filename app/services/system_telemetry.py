from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(slots=True)
class SystemTelemetrySnapshot:
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

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class SystemTelemetryService:
    def collect(self) -> SystemTelemetrySnapshot:
        cpu_percent: float | None = None
        memory_total: int | None = None
        memory_available: int | None = None
        memory_percent: float | None = None
        try:
            import psutil

            cpu_percent = float(psutil.cpu_percent(interval=0.1))
            memory = psutil.virtual_memory()
            memory_total = int(memory.total)
            memory_available = int(memory.available)
            memory_percent = float(memory.percent)
        except ImportError:
            pass

        disk = shutil.disk_usage(Path.cwd())
        disk_percent = 0.0 if disk.total == 0 else round((disk.used / disk.total) * 100, 2)
        gpu = self._collect_nvidia_gpu()

        return SystemTelemetrySnapshot(
            timestamp=datetime.now(UTC).isoformat(),
            hostname=platform.node(),
            platform=platform.platform(),
            python_version=platform.python_version(),
            cpu_count=os.cpu_count() or 1,
            cpu_percent=cpu_percent,
            memory_total_bytes=memory_total,
            memory_available_bytes=memory_available,
            memory_percent=memory_percent,
            disk_total_bytes=int(disk.total),
            disk_free_bytes=int(disk.free),
            disk_percent=disk_percent,
            process_id=os.getpid(),
            gpu_name=gpu.get("name"),
            gpu_utilization_percent=gpu.get("utilization"),
            gpu_memory_used_mb=gpu.get("memory_used"),
            gpu_memory_total_mb=gpu.get("memory_total"),
        )

    def _collect_nvidia_gpu(self) -> dict[str, float | str | None]:
        try:
            completed = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=name,utilization.gpu,memory.used,memory.total",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
        except (FileNotFoundError, subprocess.SubprocessError):
            return {"name": None, "utilization": None, "memory_used": None, "memory_total": None}

        if completed.returncode != 0 or not completed.stdout.strip():
            return {"name": None, "utilization": None, "memory_used": None, "memory_total": None}

        first_line = completed.stdout.strip().splitlines()[0]
        parts = [part.strip() for part in first_line.split(",")]
        if len(parts) != 4:
            return {"name": None, "utilization": None, "memory_used": None, "memory_total": None}

        try:
            return {
                "name": parts[0],
                "utilization": float(parts[1]),
                "memory_used": float(parts[2]),
                "memory_total": float(parts[3]),
            }
        except ValueError:
            return {"name": parts[0], "utilization": None, "memory_used": None, "memory_total": None}
