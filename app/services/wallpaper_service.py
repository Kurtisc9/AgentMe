from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class WallpaperResult:
    success: bool
    output: str


class WallpaperEngineService:
    def __init__(self, executable_path: str = "wallpaper64.exe") -> None:
        self.executable_path = executable_path

    def open_wallpaper(self, wallpaper_path: str) -> WallpaperResult:
        normalized = wallpaper_path.strip()
        if not normalized:
            raise ValueError("wallpaper_path is required.")
        return self._run(["-control", "openWallpaper", "-file", normalized])

    def pause(self) -> WallpaperResult:
        return self._run(["-control", "pause"])

    def play(self) -> WallpaperResult:
        return self._run(["-control", "play"])

    def stop(self) -> WallpaperResult:
        return self._run(["-control", "stop"])

    def _run(self, arguments: list[str]) -> WallpaperResult:
        try:
            completed = subprocess.run(
                [self.executable_path, *arguments],
                check=False,
                capture_output=True,
                text=True,
                timeout=15,
            )
        except OSError as exc:
            return WallpaperResult(success=False, output=f"Wallpaper Engine unavailable: {exc}")

        if completed.returncode != 0:
            return WallpaperResult(success=False, output=completed.stderr.strip() or "Wallpaper command failed.")
        return WallpaperResult(success=True, output=completed.stdout.strip() or "Wallpaper command sent.")
