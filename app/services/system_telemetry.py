from __future__ import annotations

import os
import platform
import shutil
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
    memory_total_bytes: int | None
    memory_available_bytes: int | None
    disk_total_bytes: int
    disk_free_bytes: int
    process_id: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class SystemTelemetryService:
    def collect(self) -> SystemTelemetrySnapshot:
        memory_total: int | None = None
        memory_available: int | None = None
        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_total = int(memory.total)
            memory_available = int(memory.available)
        except ImportError:
            pass

        disk = shutil.disk_usage(Path.cwd())
        return SystemTelemetrySnapshot(
            timestamp=datetime.now(UTC).isoformat(),
            hostname=platform.node(),
            platform=platform.platform(),
            python_version=platform.python_version(),
            cpu_count=os.cpu_count() or 1,
            memory_total_bytes=memory_total,
            memory_available_bytes=memory_available,
            disk_total_bytes=int(disk.total),
            disk_free_bytes=int(disk.free),
            process_id=os.getpid(),
        )
