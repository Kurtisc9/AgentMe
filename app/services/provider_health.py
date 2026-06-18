from __future__ import annotations

import httpx
import psycopg

from app.config import get_settings


class ProviderHealthService:
    def check_all(self) -> dict[str, bool]:
        settings = get_settings()
        return {
            "postgres": self.check_postgres(settings.postgres_url),
            "qdrant": self.check_qdrant(settings.qdrant_url),
            "ollama": self.check_ollama(settings.ollama_base_url),
            "lm_studio": self.check_lm_studio(settings.lm_studio_base_url),
        }

    def check_ollama(self, base_url: str) -> bool:
        try:
            response = httpx.get(f"{base_url.rstrip('/')}/api/tags", timeout=5.0)
            return response.is_success
        except Exception:
            return False

    def check_lm_studio(self, base_url: str) -> bool:
        try:
            response = httpx.get(f"{base_url.rstrip('/')}/models", timeout=5.0)
            return response.is_success
        except Exception:
            return False

    def check_qdrant(self, base_url: str) -> bool:
        try:
            response = httpx.get(f"{base_url.rstrip('/')}/collections", timeout=5.0)
            return response.is_success
        except Exception:
            return False

    def check_postgres(self, database_url: str) -> bool:
        try:
            with psycopg.connect(database_url, connect_timeout=5) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    return cursor.fetchone() == (1,)
        except Exception:
            return False
