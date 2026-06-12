from app.services.voice_desktop_router import VoiceDesktopRouter


class FakeDesktop:
    def __init__(self) -> None:
        self.executed: tuple[str, str | None] | None = None

    def execute(self, *, profile_id: str, approval_id: str | None = None) -> dict[str, object]:
        self.executed = (profile_id, approval_id)
        return {"profile_id": profile_id, "success": True}


def test_voice_desktop_router_matches_obs_command() -> None:
    desktop = FakeDesktop()
    router = VoiceDesktopRouter(desktop=desktop)

    result = router.route("Sage open OBS")

    assert result == {"profile_id": "pc1_obs_launch", "success": True}
    assert desktop.executed == ("pc1_obs_launch", None)


def test_voice_desktop_router_passes_approval_id() -> None:
    desktop = FakeDesktop()
    router = VoiceDesktopRouter(desktop=desktop)

    router.route("Sage start stream", approval_id="approval-1")

    assert desktop.executed == ("pc1_obs_stream_start", "approval-1")


def test_voice_desktop_router_returns_none_for_unknown_command() -> None:
    router = VoiceDesktopRouter(desktop=FakeDesktop())

    assert router.route("Sage make coffee") is None
