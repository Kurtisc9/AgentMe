from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentMe / Sage"
    environment: Literal["development", "test", "production"] = "development"
    api_host: str = "127.0.0.1"
    api_port: int = Field(default=8000, ge=1, le=65535)
    api_key: str = Field(default="replace_me", min_length=8)
    rate_limit_requests: int = Field(default=120, ge=1, le=10000)
    rate_limit_window_seconds: int = Field(default=60, ge=1, le=3600)

    embedding_provider: Literal["ollama", "lm_studio", "deterministic"] = "ollama"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    lm_studio_base_url: str = "http://127.0.0.1:1234/v1"
    lm_studio_embedding_model: str = "text-embedding-model"

    postgres_url: str = "postgresql://postgres:postgres@127.0.0.1:5432/agentme"
    qdrant_url: str = "http://127.0.0.1:6333"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SAGE_",
        extra="ignore",
    )

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("API key cannot be empty.")
        return normalized

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.environment == "production" and self.api_key in {"replace_me", "changeme", "password"}:
            raise ValueError("Production requires a non-default SAGE_API_KEY.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
