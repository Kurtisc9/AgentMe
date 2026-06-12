from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgentMe / Sage"
    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    api_key: str = "replace_me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SAGE_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
