from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.infrastructure.db.models import IntegrationRecord


class ProductRepository:
    ENTITY_TYPE = "product"

    def __init__(self, session: Session):
        self.session = session

    def _build_payload(self, payload: dict[str, Any], *, external_id: str | None) -> dict[str, Any]:
        merged = dict(payload or {})
        if external_id is not None:
            merged.setdefault("productoid", external_id)
        return merged

    def to_payload(self, record: IntegrationRecord) -> dict[str, Any]:
        payload = dict(record.payload_json or {})
        if record.external_id is not None:
            payload.setdefault("productoid", record.external_id)
        return payload

    def external_id_of(self, record: IntegrationRecord) -> str | None:
        value = record.external_id
        if value is None:
            payload = record.payload_json or {}
            value = payload.get("productoid") or payload.get("external_id") or payload.get("id")
        return str(value) if value is not None else None

    def _new_record(self, external_id: str | None, payload: dict[str, Any], operation: str) -> IntegrationRecord:
        now = datetime.utcnow()
        return IntegrationRecord(
            created_at=now,
            updated_at=now,
            entity_type=self.ENTITY_TYPE,
            operation=operation,
            external_id=external_id,
            payload_json=payload,
            status="active",
            last_error=None,
        )

    def create(self, external_id: str, payload: dict[str, Any]) -> IntegrationRecord:
        data = self._build_payload(payload, external_id=external_id)
        record = self._new_record(external_id, data, operation="create")
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(self, record: IntegrationRecord, payload: dict[str, Any]) -> IntegrationRecord:
        data = self._build_payload(payload, external_id=record.external_id)
        record.payload_json = data
        record.operation = "update"
        record.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(record)
        return record

    def upsert(self, external_id: str, payload: dict[str, Any]) -> IntegrationRecord:
        existing = self.get(external_id)
        if existing:
            return self.update(existing, payload)
        return self.create(external_id, payload)

    def delete(self, record: IntegrationRecord) -> None:
        self.session.delete(record)
        self.session.commit()

    def get(self, external_id: str) -> IntegrationRecord | None:
        stmt = select(IntegrationRecord).where(
            IntegrationRecord.entity_type == self.ENTITY_TYPE,
            IntegrationRecord.external_id == external_id,
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list(self, limit: int = 50, offset: int = 0) -> list[IntegrationRecord]:
        stmt = (
            select(IntegrationRecord)
            .where(IntegrationRecord.entity_type == self.ENTITY_TYPE)
            .order_by(IntegrationRecord.id.asc())
            .limit(limit)
            .offset(offset)
        )
        return self.session.execute(stmt).scalars().all()
