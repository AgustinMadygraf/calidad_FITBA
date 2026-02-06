from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from src.server.app.settings import settings
from src.server.infrastructure.db.session import SessionLocal
from src.server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from src.server.infrastructure.clients.mock_xubio_api_client import MockXubioApiClient
from src.server.infrastructure.clients.real_xubio_api_client import RealXubioApiClient
from src.server.infrastructure.clients.xubio_api_client import XubioApiClient


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
