from __future__ import annotations

import hashlib
import math


class EmbeddingService:
    """Deterministic local embedding fallback.

    This lightweight implementation keeps development and tests working before
    Ollama or LM Studio embedding providers are connected.
    """

    def __init__(self, dimensions: int = 64) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        normalized = text.strip().lower()
        if not normalized:
            raise ValueError("Cannot embed empty text.")

        vector = [0.0] * self.dimensions
        for token in normalized.split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]
