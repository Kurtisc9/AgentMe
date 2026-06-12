from __future__ import annotations

import httpx
import psycopg


class ProviderHealthService:
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
