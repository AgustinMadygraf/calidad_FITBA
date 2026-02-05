from __future__ import annotations

from typing import Any, Iterable
from sqlalchemy import select
from sqlalchemy.orm import Session

from server.infrastructure.db.models import IntegrationRecord


class IntegrationRecordRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        *,
        entity_type: str,
        operation: str,
        external_id: str | None,
        payload_json: dict[str, Any],
        status: str,
        last_error: str | None = None,
    ) -> IntegrationRecord:
        record = IntegrationRecord(
            entity_type=entity_type,
            operation=operation,
            external_id=external_id,
            payload_json=payload_json,
            status=status,
            last_error=last_error,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(
        self,
        record: IntegrationRecord,
        *,
        operation: str,
        payload_json: dict[str, Any] | None = None,
        status: str | None = None,
        last_error: str | None = None,
    ) -> IntegrationRecord:
        record.operation = operation
        if payload_json is not None:
            record.payload_json = payload_json
        if status is not None:
            record.status = status
        record.last_error = last_error
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete(self, record: IntegrationRecord) -> None:
        self.session.delete(record)
        self.session.commit()

    def get_by_external_id(self, entity_type: str, external_id: str) -> IntegrationRecord | None:
        stmt = select(IntegrationRecord).where(
            IntegrationRecord.entity_type == entity_type,
            IntegrationRecord.external_id == external_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list(
        self,
        *,
        entity_type: str,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Iterable[IntegrationRecord]:
        stmt = select(IntegrationRecord).where(IntegrationRecord.entity_type == entity_type)
        if status:
            stmt = stmt.where(IntegrationRecord.status == status)
        stmt = stmt.limit(limit).offset(offset)
        return self.session.execute(stmt).scalars().all()
