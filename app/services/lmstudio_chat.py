from __future__ import annotations

import httpx


class LMStudioChatService:
    def __init__(self, base_url: str = "http://127.0.0.1:1234/v1", timeout_seconds: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, *, model: str, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise RuntimeError("LM Studio returned no choices.")
        message = choices[0].get("message", {})
        text = message.get("content")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("LM Studio returned no response.")
        return text.strip()
