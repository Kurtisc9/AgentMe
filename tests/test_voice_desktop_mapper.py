import json
from pathlib import Path

from app.services.desktop_profile_service import DesktopProfileService
from app.services.voice_desktop_mapper import VoiceDesktopMapper


def test_voice_command_maps_to_profile(tmp_path: Path) -> None:
    path = tmp_path / "profiles.json"
    path.write_text(
        json.dumps({
            "profiles": [
                {
                    "id": "open_obs",
                    "name": "OBS Studio",
                    "type": "application",
                    "risk_level": "LOW",
                    "command": "obs64.exe",
                    "arguments": [],
                    "device": "PC1",
                    "favorite": True,
                }
            ]
        }),
        encoding="utf-8",
    )

    mapper = VoiceDesktopMapper(DesktopProfileService(path))

    assert mapper.match_profile_id("launch OBS Studio") == "open_obs"
    assert mapper.match_profile_id("unknown command") is None
