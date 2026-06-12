from __future__ import annotations

from app.services.desktop_control_service import DesktopControlService


class VoiceDesktopRouter:
    def __init__(self, desktop: DesktopControlService | None = None) -> None:
        self.desktop = desktop or DesktopControlService()

    def route(self, text: str, approval_id: str | None = None) -> dict[str, object] | None:
        normalized = text.strip().lower()
        if not normalized:
            return None

        command_map = {
            "open obs": "pc1_obs_launch",
            "start recording": "pc1_obs_start_recording",
            "stop recording": "pc1_obs_stop_recording",
            "start stream": "pc1_obs_stream_start",
            "stop stream": "pc1_obs_stream_stop",
            "open wallpaper engine": "pc1_wallpaper_launch",
            "pause wallpaper": "pc1_wallpaper_pause",
            "play wallpaper": "pc1_wallpaper_play",
            "open agentme": "pc1_agentme_repo",
            "open display settings": "pc1_display_settings",
        }

        profile_id = next((value for phrase, value in command_map.items() if phrase in normalized), None)
        if profile_id is None:
            return None
        return self.desktop.execute(profile_id=profile_id, approval_id=approval_id)
