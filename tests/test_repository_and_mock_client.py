from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.db.models import Base
from src.infrastructure.repositories.integration_record_repository import (
    ProductRepository,
)
from src.interface_adapter.gateways.mock_xubio_api_client import MockXubioApiClient
from src.entities.schemas import ProductCreate, ProductUpdate


def _make_repo() -> ProductRepository:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    return ProductRepository(session)


def test_repository_crud() -> None:
    repo = _make_repo()
    record = repo.create("p-1", {"productoid": "p-1", "nombre": "Test"})
    assert record.productoid == "p-1"
    assert repo.get("p-1") is not None

    repo.update(record, {"productoid": "p-1", "nombre": "Updated"})
    updated = repo.get("p-1")
    assert updated is not None
    assert updated.nombre == "Updated"

    items = list(repo.list(limit=10, offset=0))
    assert len(items) == 1

    repo.delete(record)
    assert repo.get("p-1") is None


def test_mock_client_create_update_delete() -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    created = client.create_product(ProductCreate(external_id="p-2", name="Producto", sku="SKU", price=10.0))
    assert created.external_id == "p-2"

    updated = client.update_product("p-2", ProductUpdate(name="Nuevo"))
    assert updated.name == "Nuevo"

    fetched = client.get_product("p-2")
    assert fetched.external_id == "p-2"

    items = client.list_products()
    assert len(items) == 1

    client.delete_product("p-2")
    assert client.list_products() == []


def test_mock_client_create_overwrites_existing() -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    client.create_product(ProductCreate(external_id="p-9", name="A"))
    updated = client.create_product(ProductCreate(external_id="p-9", name="B"))
    assert updated.name == "B"
