from __future__ import annotations

from typing import Any

from src.use_case.use_cases import (
    CreateProduct,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    SyncPullProduct,
)
from src.entities.schemas import ProductCreate, ProductOut, ProductUpdate


class _FakeClient:
    def __init__(self) -> None:
        self.items: dict[str, ProductOut] = {}
        self.deleted: list[str] = []

    def create_product(self, payload: ProductCreate) -> ProductOut:
        out = ProductOut(external_id=payload.external_id or "gen", name=payload.name, sku=payload.sku, price=payload.price)
        self.items[out.external_id] = out
        return out

    def update_product(self, external_id: str, payload: ProductUpdate) -> ProductOut:
        current = self.items.get(external_id) or ProductOut(external_id=external_id, name="X")
        updated = current.model_copy(update=payload.model_dump(exclude_none=True))
        self.items[external_id] = updated
        return updated

    def delete_product(self, external_id: str) -> None:
        self.deleted.append(external_id)
        self.items.pop(external_id, None)

    def get_product(self, external_id: str) -> ProductOut:
        return self.items[external_id]

    def list_products(self, limit: int = 50, offset: int = 0) -> list[ProductOut]:
        _ = (limit, offset)
        return list(self.items.values())


class _FakeRepo:
    def __init__(self) -> None:
        self.created: list[dict[str, Any]] = []
        self.records: list[dict[str, Any]] = []

    def list(self, limit: int = 50, offset: int = 0):
        _ = (limit, offset)
        return self.records

    def upsert(self, productoid: str, payload: dict[str, Any]):
        existing = next((r for r in self.records if r["productoid"] == productoid), None)
        if existing:
            existing.update(payload)
            return existing
        payload = dict(payload)
        payload["productoid"] = productoid
        self.created.append(payload)
        self.records.append(payload)
        return payload


def test_use_cases_basic_crud() -> None:
    client = _FakeClient()
    create = CreateProduct(client).execute(ProductCreate(external_id="p-1", name="Prod"))
    assert create.external_id == "p-1"

    updated = UpdateProduct(client).execute("p-1", ProductUpdate(name="Nuevo"))
    assert updated.name == "Nuevo"

    fetched = GetProduct(client).execute("p-1")
    assert fetched.external_id == "p-1"

    listed = ListProducts(client).execute()
    assert len(listed) == 1

    DeleteProduct(client).execute("p-1")
    assert client.deleted == ["p-1"]


def test_sync_pull_product_mock() -> None:
    client = _FakeClient()
    repo = _FakeRepo()
    result = SyncPullProduct(client, repo).execute(is_mock=True)
    assert result["status"] == "ok"
    assert repo.created


def test_sync_pull_product_real_path() -> None:
    class _Client:
        def list_products(self):
            return [
                ProductOut(external_id="p-1", name="A"),
                ProductOut(external_id="p-2", name="B"),
            ]

    repo = _FakeRepo()
    result = SyncPullProduct(_Client(), repo).execute(is_mock=False)
    assert result["status"] == "ok"
    assert len(repo.created) == 2
