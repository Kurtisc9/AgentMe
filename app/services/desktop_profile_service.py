from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DesktopProfile:
    id: str
    name: str
    type: str
    risk_level: str
    command: str
    arguments: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "risk_level": self.risk_level,
            "command": self.command,
            "arguments": self.arguments,
        }


class DesktopProfileService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("config/desktop_profiles.json")

    def list_profiles(self) -> list[DesktopProfile]:
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return [DesktopProfile(**item) for item in payload.get("profiles", [])]

    def get_profile(self, profile_id: str) -> DesktopProfile:
        profile = next((item for item in self.list_profiles() if item.id == profile_id), None)
        if profile is None:
            raise KeyError(f"Unknown desktop profile: {profile_id}")
        return profile
