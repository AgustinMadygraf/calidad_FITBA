from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class ClientSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    base_url: str = "http://localhost:8000"
    xubio_mode: str = "mock"


settings = ClientSettings()
