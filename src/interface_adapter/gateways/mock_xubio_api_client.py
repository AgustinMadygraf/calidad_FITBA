from __future__ import annotations

from typing import Any

from src.entities.schemas import ProductCreate, ProductOut, ProductUpdate
from src.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)


class MockXubioApiClient:
    def __init__(self, repository: IntegrationRecordRepository):
        self.repository = repository

    def _build_xubio_payload(
        self,
        *,
        existing_payload: dict[str, Any] | None,
        payload: ProductCreate | ProductUpdate,
        external_id: str,
    ) -> dict[str, Any]:
        raw_payload = dict(getattr(payload, "xubio_payload", None) or {})
        merged = dict(existing_payload or {})
        merged.update(raw_payload)
        merged["productoid"] = external_id
        if getattr(payload, "name", None) is not None:
            merged["nombre"] = payload.name
        if getattr(payload, "sku", None) is not None:
            merged["codigo"] = payload.sku
        if getattr(payload, "price", None) is not None:
            merged["precioVenta"] = payload.price
        return merged

    def _to_product_out(self, payload: dict[str, Any], external_id: str) -> ProductOut:
        name = payload.get("nombre") or payload.get("name") or payload.get("descripcion") or "SIN_NOMBRE"
        sku = payload.get("codigo") or payload.get("sku")
        price = payload.get("precioVenta")
        if price is None:
            price = payload.get("precioUltCompra") or payload.get("price")
        return ProductOut(
            external_id=str(external_id),
            name=name,
            sku=sku,
            price=price,
            xubio_payload=payload,
        )

    def create_product(self, payload: ProductCreate) -> ProductOut:
        external_id = payload.external_id
        if not external_id and payload.xubio_payload:
            external_id = payload.xubio_payload.get("productoid")
        external_id = str(external_id) if external_id is not None else None

        if external_id:
            existing = self.repository.get_by_external_id("product", external_id)
            if existing:
                updated_payload = self._build_xubio_payload(
                    existing_payload=existing.payload_json,
                    payload=payload,
                    external_id=external_id,
                )
                self.repository.update(
                    existing,
                    operation="update",
                    payload_json=updated_payload,
                    status="local",
                )
                return self._to_product_out(updated_payload, external_id)

        external_id = external_id or f"local-{id(payload)}"
        record_payload = self._build_xubio_payload(
            existing_payload=None,
            payload=payload,
            external_id=external_id,
        )
        self.repository.create(
            entity_type="product",
            operation="create",
            external_id=external_id,
            payload_json=record_payload,
            status="local",
        )
        return self._to_product_out(record_payload, external_id)

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        existing = self.repository.get_by_external_id("product", external_id)
        if not existing:
            raise ValueError("Producto no encontrado")
        updated_payload = self._build_xubio_payload(
            existing_payload=existing.payload_json,
            payload=payload,
            external_id=external_id,
        )
        self.repository.update(
            existing,
            operation="update",
            payload_json=updated_payload,
            status="local",
        )
        return self._to_product_out(updated_payload, external_id)

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
        return self._to_product_out(payload, external_id)

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        records = self.repository.list(
            entity_type="product",
            limit=limit,
            offset=offset,
        )
        items: list[ProductOut] = []
        for record in records:
            payload = dict(record.payload_json)
            external_id = record.external_id or payload.get("external_id") or payload.get("productoid") or ""
            items.append(self._to_product_out(payload, str(external_id)))
        return items
