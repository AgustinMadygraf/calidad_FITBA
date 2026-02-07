from __future__ import annotations

from src.entities.schemas import ProductCreate, ProductOut, ProductUpdate
from src.interface_adapter.gateways.xubio_api_client import XubioApiClient
from src.interface_adapter.presenters.product_presenter import to_xubio as present_product_to_xubio


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
                if not list(self.repository.list(limit=1, offset=0)):
                    self.repository.upsert(
                        "demo-1",
                        {"productoid": "demo-1", "nombre": "Producto demo"},
                    )
                return {"status": "ok"}

            items = self.client.list_products()
            for item in items:
                payload = present_product_to_xubio(item)
                self.repository.upsert(str(item.external_id), payload)
            return {"status": "ok"}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}
