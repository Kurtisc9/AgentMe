from app.services.wake_phrase_service import WakePhraseService


def test_detects_direct_wake_phrase() -> None:
    detector = WakePhraseService("Sage")

    assert detector.strip_wake_phrase("Sage, review this code") == "review this code"


def test_detects_hey_sage() -> None:
    detector = WakePhraseService("Sage")

    assert detector.strip_wake_phrase("Hey Sage open the dashboard") == "open the dashboard"


def test_returns_none_when_wake_phrase_missing() -> None:
    detector = WakePhraseService("Sage")

    assert detector.strip_wake_phrase("Open the dashboard") is None
