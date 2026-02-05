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


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_create_and_list_api(monkeypatch):
    uow = FakeUoW()

    def _uow_factory():
        return uow

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/res-partners",
            json={"name": "Ana", "email": "ana@example.com"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "ana@example.com"

        r = await client.get("/api/v1/res-partners")
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 1

        r = await client.put(f"/api/v1/res-partners/{data['id']}", json={"name": "Ana B"})
        assert r.status_code == 200

        r = await client.delete(f"/api/v1/res-partners/{data['id']}")
        assert r.status_code == 204
