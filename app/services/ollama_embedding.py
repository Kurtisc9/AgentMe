from __future__ import annotations

import httpx


class OllamaEmbeddingService:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "nomic-embed-text",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def embed(self, text: str) -> list[float]:
        normalized = text.strip()
        if not normalized:
            raise ValueError("Cannot embed empty text.")

        response = httpx.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": normalized},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        embedding = payload.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Ollama returned no embedding.")
        return [float(value) for value in embedding]
