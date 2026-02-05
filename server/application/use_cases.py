from __future__ import annotations

from shared.schemas import ProductCreate, ProductOut, ProductUpdate
from server.infrastructure.clients.xubio_api_client import XubioApiClient


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
