from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import BigInteger, DateTime, Index, Integer, JSON, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationRecord(Base):
    __tablename__ = "productoVenta"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    operation: Mapped[str] = mapped_column(String(20))
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    payload_json: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20))
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)


Index("ix_entity_external", IntegrationRecord.entity_type, IntegrationRecord.external_id)
Index("ix_entity_status", IntegrationRecord.entity_type, IntegrationRecord.status)
