from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentMe / Sage"
    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_key: str = "replace_me"

    embedding_provider: str = "ollama"
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
