from __future__ import annotations

from app.services.desktop_profile_service import DesktopProfileService


class VoiceDesktopMapper:
    def __init__(self, profiles: DesktopProfileService | None = None) -> None:
        self.profiles = profiles or DesktopProfileService()

    def match_profile_id(self, command: str) -> str | None:
        normalized = command.strip().lower()
        if not normalized:
            return None

        for profile in self.profiles.list_profiles():
            phrases = {
                profile.id.lower().replace("_", " "),
                profile.name.lower(),
                f"open {profile.name.lower()}",
                f"launch {profile.name.lower()}",
                f"start {profile.name.lower()}",
                f"run {profile.name.lower()}",
            }
            if normalized in phrases:
                return profile.id
        return None
