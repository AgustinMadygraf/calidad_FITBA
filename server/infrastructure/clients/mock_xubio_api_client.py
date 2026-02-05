from __future__ import annotations

from typing import Any

from shared.schemas import ProductCreate, ProductOut, ProductUpdate
from server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)


class MockXubioApiClient:
    def __init__(self, repository: IntegrationRecordRepository):
        self.repository = repository

    def create_product(self, payload: ProductCreate) -> ProductOut:
        if payload.external_id:
            existing = self.repository.get_by_external_id("product", payload.external_id)
            if existing:
                updated_payload = {**existing.payload_json, **payload.model_dump(exclude_none=True)}
                self.repository.update(
                    existing,
                    operation="update",
                    payload_json=updated_payload,
                    status="local",
                )
                return ProductOut(**updated_payload, external_id=payload.external_id)

        external_id = payload.external_id or f"local-{id(payload)}"
        record_payload: dict[str, Any] = payload.model_dump()
        record_payload["external_id"] = external_id
        self.repository.create(
            entity_type="product",
            operation="create",
            external_id=external_id,
            payload_json=record_payload,
            status="local",
        )
        return ProductOut(**record_payload, external_id=external_id)

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        existing = self.repository.get_by_external_id("product", external_id)
        if not existing:
            raise ValueError("Producto no encontrado")
        updated_payload = {**existing.payload_json, **payload.model_dump(exclude_none=True)}
        updated_payload["external_id"] = external_id
        self.repository.update(
            existing,
            operation="update",
            payload_json=updated_payload,
            status="local",
        )
        return ProductOut(**updated_payload, external_id=external_id)

    def delete_product(self, external_id: str) -> None:
        existing = self.repository.get_by_external_id("product", external_id)
        if not existing:
            raise ValueError("Producto no encontrado")
        self.repository.delete(existing)

    def get_product(self, external_id: str) -> ProductOut:
        existing = self.repository.get_by_external_id("product", external_id)
        if not existing:
            raise ValueError("Producto no encontrado")
        payload = dict(existing.payload_json)
        payload["external_id"] = external_id
        return ProductOut(**payload, external_id=external_id)

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        records = self.repository.list(
            entity_type="product",
            limit=limit,
            offset=offset,
        )
        items: list[ProductOut] = []
        for record in records:
            payload = dict(record.payload_json)
            external_id = record.external_id or payload.get("external_id") or ""
            payload["external_id"] = external_id
            items.append(ProductOut(**payload, external_id=external_id))
        return items
