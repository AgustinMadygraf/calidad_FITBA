from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "mysql+pymysql://user:pass@localhost:3306/xubio_like"
    is_xubio_mode_mock: bool = True
    xubio_client_id: str | None = None
    xubio_secret_id: str | None = None
    disable_delete_in_real: bool = True
    port: int = 8000

    @field_validator("is_xubio_mode_mock", mode="before")
    @classmethod
    def _validate_bool(cls, value: object) -> object:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "false", "1", "0", "yes", "no"}:
                return normalized in {"true", "1", "yes"}
        raise ValueError("IS_XUBIO_MODE_MOCK debe ser booleano (true/false).")


settings = Settings()
