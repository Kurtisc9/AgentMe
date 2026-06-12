from __future__ import annotations


class WakePhraseService:
    def __init__(self, wake_phrase: str = "Sage") -> None:
        normalized = wake_phrase.strip()
        if not normalized:
            raise ValueError("Wake phrase cannot be empty.")
        self.wake_phrase = normalized.lower()

    def strip_wake_phrase(self, text: str) -> str | None:
        normalized = text.strip()
        if not normalized:
            return None

        lowered = normalized.lower()
        if lowered == self.wake_phrase:
            return ""

        prefixes = (
            f"{self.wake_phrase},",
            f"{self.wake_phrase} ",
            f"hey {self.wake_phrase}",
            f"okay {self.wake_phrase}",
        )
        for prefix in prefixes:
            if lowered.startswith(prefix):
                return normalized[len(prefix):].lstrip(" ,:-")
        return None
