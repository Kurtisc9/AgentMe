from __future__ import annotations

from app.services.desktop_control_service import DesktopControlService
from app.services.desktop_profile_service import DesktopProfileService
from app.services.wake_phrase_service import WakePhraseService


class VoiceDesktopService:
    def __init__(
        self,
        *,
        desktop: DesktopControlService | None = None,
        profiles: DesktopProfileService | None = None,
        wake_phrase: str = "Sage",
    ) -> None:
        self.desktop = desktop or DesktopControlService()
        self.profiles = profiles or self.desktop.profiles
        self.detector = WakePhraseService(wake_phrase)

    def route(self, *, text: str, approval_id: str | None = None) -> dict[str, object]:
        command = self.detector.strip_wake_phrase(text)
        if command is None:
            command = text.strip()
        normalized = command.lower().strip()
        if not normalized:
            return {
                "matched": False,
                "profile_id": None,
                "result": None,
                "reason": "No desktop command detected.",
            }

        profiles = self.profiles.list_profiles()
        scored: list[tuple[int, str]] = []
        for profile in profiles:
            haystack = " ".join([profile.id, profile.name, profile.type, profile.command]).lower()
            score = sum(1 for word in normalized.split() if word in haystack)
            if score > 0:
                scored.append((score, profile.id))

        if not scored:
            return {
                "matched": False,
                "profile_id": None,
                "result": None,
                "reason": "No matching desktop profile found.",
            }

        profile_id = sorted(scored, reverse=True)[0][1]
        result = self.desktop.execute(profile_id=profile_id, approval_id=approval_id)
        return {
            "matched": True,
            "profile_id": profile_id,
            "result": result,
            "reason": "Desktop command routed.",
        }
