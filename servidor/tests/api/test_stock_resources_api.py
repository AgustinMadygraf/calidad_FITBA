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
async def test_create_and_list_stock_resources(monkeypatch):
    uow = FakeUoW()

    def _uow_factory():
        return uow

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        partner = await client.post("/api/v1/res-partners", json={"name": "Cliente"})
        assert partner.status_code == 201
        partner_id = partner.json()["id"]

        picking = await client.post(
            "/api/v1/stock-pickings", json={"name": "OUT/0001", "partner_id": partner_id}
        )
        assert picking.status_code == 201
        picking_id = picking.json()["id"]

        package_type = await client.post(
            "/api/v1/stock-package-types", json={"name": "Caja A", "weight": 0.5}
        )
        assert package_type.status_code == 201
        package_type_id = package_type.json()["id"]

        package = await client.post(
            "/api/v1/stock-quant-packages",
            json={
                "name": "PACK0001",
                "package_type_id": package_type_id,
                "shipping_weight": 10.0,
                "picking_id": picking_id,
            },
        )
        assert package.status_code == 201

        r = await client.get("/api/v1/stock-pickings")
        assert r.status_code == 200
        assert len(r.json()["items"]) == 1

        r = await client.put(f"/api/v1/stock-pickings/{picking_id}", json={"name": "OUT/0002"})
        assert r.status_code == 200

        r = await client.put(
            f"/api/v1/stock-package-types/{package_type_id}", json={"weight": 0.75}
        )
        assert r.status_code == 200

        r = await client.put(
            f"/api/v1/stock-quant-packages/{package.json()['id']}",
            json={"shipping_weight": 11.0},
        )
        assert r.status_code == 200

        r = await client.get("/api/v1/stock-package-types")
        assert r.status_code == 200
        assert len(r.json()["items"]) == 1

        r = await client.get("/api/v1/stock-quant-packages")
        assert r.status_code == 200
        assert len(r.json()["items"]) == 1

        r = await client.delete(f"/api/v1/stock-quant-packages/{package.json()['id']}")
        assert r.status_code == 204

        r = await client.delete(f"/api/v1/stock-package-types/{package_type_id}")
        assert r.status_code == 204

        r = await client.delete(f"/api/v1/stock-pickings/{picking_id}")
        assert r.status_code == 204
