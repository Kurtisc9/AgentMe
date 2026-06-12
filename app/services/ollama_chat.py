from __future__ import annotations

import httpx


class OllamaChatService:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout_seconds: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def generate(self, *, model: str, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload.get("response")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("Ollama returned no response.")
        return text.strip()
