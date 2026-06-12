from __future__ import annotations

import httpx


class LMStudioEmbeddingService:
    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:1234/v1",
        model: str = "text-embedding-model",
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
            f"{self.base_url}/embeddings",
            json={"model": self.model, "input": normalized},
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise RuntimeError("LM Studio returned no embedding data.")
        embedding = data[0].get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("LM Studio returned no embedding.")
        return [float(value) for value in embedding]
