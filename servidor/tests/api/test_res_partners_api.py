import pytest

httpx = pytest.importorskip("httpx")

from infrastructure.repositories.in_memory_res_partner_repository import InMemoryResPartnerRepository
from infrastructure.repositories.in_memory_stock_picking_repository import InMemoryStockPickingRepository
from infrastructure.repositories.in_memory_stock_package_type_repository import InMemoryStockPackageTypeRepository
from infrastructure.repositories.in_memory_stock_quant_package_repository import InMemoryStockQuantPackageRepository
from application.ports.unit_of_work import IUnitOfWork
from servidor.app.main import create_app


class FakeUoW(IUnitOfWork):
    def __init__(self) -> None:
        self.partners = InMemoryResPartnerRepository()
        self.pickings = InMemoryStockPickingRepository()
        self.package_types = InMemoryStockPackageTypeRepository()
        self.packages = InMemoryStockQuantPackageRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


def test_create_and_list_api(monkeypatch):
    def _uow_factory():
        return FakeUoW()

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()

    transport = httpx.ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://test") as client:
        r = client.post(
            "/api/v1/res-partners",
            json={"name": "Ana", "email": "ana@example.com"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "ana@example.com"

        r = client.get("/api/v1/res-partners")
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 1
