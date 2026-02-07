from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from src.server.app.settings import settings
from src.infrastructure.db.session import SessionLocal
from src.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from src.interface_adapter.gateways.mock_xubio_api_client import MockXubioApiClient
from src.interface_adapter.gateways.real_xubio_api_client import RealXubioApiClient
from src.interface_adapter.gateways.xubio_api_client import XubioApiClient


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_xubio_client(db: Session) -> XubioApiClient:
    if settings.IS_PROD:
        return RealXubioApiClient()
    repository = IntegrationRecordRepository(db)
    return MockXubioApiClient(repository)
