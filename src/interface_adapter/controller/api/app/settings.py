from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.shared.config import parse_bool

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "mysql+pymysql://user:pass@localhost:3306/xubio_like"
    IS_PROD: bool = False
    xubio_client_id: str | None = None
    xubio_secret_id: str | None = None
    disable_delete_in_real: bool = True
    port: int = 8000

    @field_validator("IS_PROD", mode="before")
    @classmethod
    def _validate_bool(cls, value: object) -> object:
        return parse_bool(value, "IS_PROD")


settings = Settings()
