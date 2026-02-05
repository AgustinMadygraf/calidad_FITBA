from __future__ import annotations

from typing import Protocol

from shared.schemas import ProductCreate, ProductOut, ProductUpdate


class XubioApiClient(Protocol):
    def create_product(self, payload: ProductCreate) -> ProductOut:
        ...

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        ...

    def delete_product(self, external_id: str) -> None:
        ...

    def get_product(self, external_id: str) -> ProductOut:
        ...

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        ...
