from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.server.infrastructure.db.models import Base
from src.server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from src.server.infrastructure.clients.mock_xubio_api_client import MockXubioApiClient
from src.shared.schemas import ProductCreate, ProductUpdate


def _make_repo() -> IntegrationRecordRepository:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    return IntegrationRecordRepository(session)


def test_repository_crud() -> None:
    repo = _make_repo()
    record = repo.create(
        entity_type="product",
        operation="create",
        external_id="p-1",
        payload_json={"external_id": "p-1", "name": "Test"},
        status="local",
    )
    assert record.id is not None
    assert repo.get_by_external_id("product", "p-1") is not None

    repo.update(record, operation="update", payload_json={"external_id": "p-1", "name": "Updated"}, status="synced")
    updated = repo.get_by_external_id("product", "p-1")
    assert updated is not None
    assert updated.payload_json["name"] == "Updated"

    items = list(repo.list(entity_type="product", status="synced", limit=10, offset=0))
    assert len(items) == 1

    repo.delete(record)
    assert repo.get_by_external_id("product", "p-1") is None


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
