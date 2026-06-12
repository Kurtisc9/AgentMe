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
    device: str = "PC1"
    favorite: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "risk_level": self.risk_level,
            "command": self.command,
            "arguments": self.arguments,
            "device": self.device,
            "favorite": self.favorite,
        }


class DesktopProfileService:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path("config/desktop_profiles.json")
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list_profiles(self, *, device: str | None = None) -> list[DesktopProfile]:
        payload = self._read_payload()
        profiles = [DesktopProfile(**item) for item in payload.get("profiles", [])]
        if device:
            profiles = [profile for profile in profiles if profile.device == device]
        return profiles

    def get_profile(self, profile_id: str) -> DesktopProfile:
        profile = next((item for item in self.list_profiles() if item.id == profile_id), None)
        if profile is None:
            raise KeyError(f"Unknown desktop profile: {profile_id}")
        return profile

    def create_or_update(self, profile: DesktopProfile) -> DesktopProfile:
        payload = self._read_payload()
        profiles = [DesktopProfile(**item) for item in payload.get("profiles", [])]
        profiles = [item for item in profiles if item.id != profile.id]
        profiles.append(profile)
        self._write_profiles(profiles)
        return profile

    def delete(self, profile_id: str) -> None:
        profiles = self.list_profiles()
        filtered = [profile for profile in profiles if profile.id != profile_id]
        if len(filtered) == len(profiles):
            raise KeyError(f"Unknown desktop profile: {profile_id}")
        self._write_profiles(filtered)

    def _read_payload(self) -> dict[str, object]:
        if not self.path.exists():
            return {"profiles": []}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write_profiles(self, profiles: list[DesktopProfile]) -> None:
        payload = {"profiles": [profile.to_dict() for profile in profiles]}
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
