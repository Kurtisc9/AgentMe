from __future__ import annotations

import json
from dataclasses import dataclass
from urllib import request


@dataclass(slots=True)
class OBSResult:
    success: bool
    output: str


class OBSService:
    """OBS control foundation.

    This is intentionally adapter-based. It can call an OBS control bridge over HTTP
    now, and can be swapped to native obs-websocket later without changing APIs.
    """

    def __init__(self, bridge_url: str = "http://127.0.0.1:4456") -> None:
        self.bridge_url = bridge_url.rstrip("/")

    def start_streaming(self) -> OBSResult:
        return self._post("/obs/start-streaming", {})

    def stop_streaming(self) -> OBSResult:
        return self._post("/obs/stop-streaming", {})

    def start_recording(self) -> OBSResult:
        return self._post("/obs/start-recording", {})

    def stop_recording(self) -> OBSResult:
        return self._post("/obs/stop-recording", {})

    def switch_scene(self, scene_name: str) -> OBSResult:
        normalized = scene_name.strip()
        if not normalized:
            raise ValueError("scene_name is required.")
        return self._post("/obs/switch-scene", {"scene_name": normalized})

    def _post(self, path: str, payload: dict[str, object]) -> OBSResult:
        data = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            f"{self.bridge_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=10) as response:
                body = response.read().decode("utf-8")
        except Exception as exc:
            return OBSResult(success=False, output=f"OBS bridge unavailable: {exc}")
        return OBSResult(success=True, output=body or "OBS command sent.")
