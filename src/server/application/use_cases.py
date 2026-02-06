from __future__ import annotations

from src.shared.schemas import ProductCreate, ProductOut, ProductUpdate
from src.server.infrastructure.clients.xubio_api_client import XubioApiClient


class CreateProduct:
    def __init__(self, client: XubioApiClient):
        self.client = client

    def execute(self, payload: ProductCreate) -> ProductOut:
        return self.client.create_product(payload)


class UpdateProduct:
    def __init__(self, client: XubioApiClient):
        self.client = client

    def execute(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        return self.client.update_product(external_id, payload)


class DeleteProduct:
    def __init__(self, client: XubioApiClient):
        self.client = client

    def execute(self, external_id: str) -> None:
        return self.client.delete_product(external_id)


class GetProduct:
    def __init__(self, client: XubioApiClient):
        self.client = client

    def execute(self, external_id: str) -> ProductOut:
        return self.client.get_product(external_id)


class ListProducts:
    def __init__(self, client: XubioApiClient):
        self.client = client

    def execute(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        return self.client.list_products(limit=limit, offset=offset)


class SyncPullProduct:
    def __init__(self, client: XubioApiClient, repository) -> None:
        self.client = client
        self.repository = repository

    def execute(self, is_mock: bool) -> dict[str, str]:
        try:
            if is_mock:
                if not list(self.repository.list(entity_type="product", limit=1, offset=0)):
                    self.repository.create(
                        entity_type="product",
                        operation="create",
                        external_id="demo-1",
                        payload_json={"external_id": "demo-1", "name": "Producto demo"},
                        status="synced",
                    )
                return {"status": "ok"}

            items = self.client.list_products()
            for item in items:
                existing = self.repository.get_by_external_id("product", item.external_id)
                payload = item.model_dump()
                if existing:
                    self.repository.update(existing, operation="update", payload_json=payload, status="synced")
                else:
                    self.repository.create(
                        entity_type="product",
                        operation="create",
                        external_id=item.external_id,
                        payload_json=payload,
                        status="synced",
                    )
            return {"status": "ok"}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}
