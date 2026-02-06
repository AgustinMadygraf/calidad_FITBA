from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from server.app.settings import settings
from server.infrastructure.db.session import SessionLocal
from server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from server.infrastructure.clients.mock_xubio_api_client import MockXubioApiClient
from server.infrastructure.clients.real_xubio_api_client import RealXubioApiClient
from server.infrastructure.clients.xubio_api_client import XubioApiClient


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_xubio_client(db: Session) -> XubioApiClient:
    if not settings.IS_XUBIO_MODE_DEV:
        return RealXubioApiClient()
    repository = IntegrationRecordRepository(db)
    return MockXubioApiClient(repository)
