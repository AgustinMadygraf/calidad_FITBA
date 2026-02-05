from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "mysql+pymysql://user:pass@localhost:3306/xubio_like"
    xubio_mode: str = "mock"  # mock | real
    xubio_base_url: str = "https://xubio.com/API/1.1"
    xubio_token_endpoint: str = "https://xubio.com/API/1.1/TokenEndpoint"
    xubio_client_id: str | None = None
    xubio_secret_id: str | None = None
    xubio_product_endpoint: str = "/Products"  # TODO: confirmar endpoint real
    disable_delete_in_real: bool = True


settings = Settings()
