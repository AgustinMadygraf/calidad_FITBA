from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.shared.config import parse_bool

class ClientSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    base_url: str = "http://localhost:8000"
    IS_PROD: bool = False
    xubio_client_id: str | None = None
    xubio_secret_id: str | None = None

    @field_validator("IS_PROD", mode="before")
    @classmethod
    def _validate_bool(cls, value: object) -> object:
        return parse_bool(value, "IS_PROD")


settings = ClientSettings()
