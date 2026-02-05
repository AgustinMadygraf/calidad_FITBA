import pytest

httpx = pytest.importorskip("httpx")

from infrastructure.repositories.in_memory_res_partner_repository import InMemoryResPartnerRepository
from infrastructure.repositories.in_memory_stock_picking_repository import InMemoryStockPickingRepository
from infrastructure.repositories.in_memory_stock_package_type_repository import InMemoryStockPackageTypeRepository
from infrastructure.repositories.in_memory_stock_quant_package_repository import InMemoryStockQuantPackageRepository
from application.ports.unit_of_work import IUnitOfWork
from servidor.app.main import create_app
from application.exceptions import DatabaseError
import servidor.app.routers.res_partners as res_partners_router
import servidor.app.routers.stock_pickings as stock_pickings_router
import servidor.app.routers.stock_package_types as stock_package_types_router
import servidor.app.routers.stock_quant_packages as stock_quant_packages_router


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
async def test_not_found_and_validation_paths(monkeypatch):
    uow = FakeUoW()

    def _uow_factory():
        return uow

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/res-partners/999")
        assert r.status_code == 404

        r = await client.post("/api/v1/res-partners", json={"name": ""})
        assert r.status_code == 400

        r = await client.put("/api/v1/stock-pickings/999", json={"name": "OUT/9"})
        assert r.status_code == 404

        r = await client.post("/api/v1/stock-pickings", json={"name": "", "partner_id": 1})
        assert r.status_code == 400

        r = await client.post(
            "/api/v1/stock-package-types",
            json={"name": "Caja", "weight": -1},
        )
        assert r.status_code in (400, 422)

        r = await client.get("/api/v1/stock-package-types/999")
        assert r.status_code == 404

        r = await client.post(
            "/api/v1/stock-quant-packages",
            json={"name": "PACK", "package_type_id": 0, "picking_id": 0, "shipping_weight": 1},
        )
        assert r.status_code in (400, 422)

        r = await client.get("/api/v1/stock-quant-packages/999")
        assert r.status_code == 404


@pytest.mark.anyio
async def test_database_error_paths(monkeypatch):
    uow = FakeUoW()

    def _uow_factory():
        return uow

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    def _raise_db(*args, **kwargs):
        raise DatabaseError("db")

    monkeypatch.setattr(res_partners_router.CreateResPartner, "execute", _raise_db)
    monkeypatch.setattr(stock_pickings_router.CreateStockPicking, "execute", _raise_db)
    monkeypatch.setattr(stock_package_types_router.CreateStockPackageType, "execute", _raise_db)
    monkeypatch.setattr(stock_quant_packages_router.CreateStockQuantPackage, "execute", _raise_db)
    monkeypatch.setattr(res_partners_router.ListResPartners, "execute", _raise_db)
    monkeypatch.setattr(stock_pickings_router.ListStockPickings, "execute", _raise_db)
    monkeypatch.setattr(stock_package_types_router.ListStockPackageTypes, "execute", _raise_db)
    monkeypatch.setattr(stock_quant_packages_router.ListStockQuantPackages, "execute", _raise_db)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/res-partners", json={"name": "X"})
        assert r.status_code == 500
        r = await client.post("/api/v1/stock-pickings", json={"name": "OUT/1", "partner_id": 1})
        assert r.status_code == 500
        r = await client.post("/api/v1/stock-package-types", json={"name": "Caja", "weight": 0})
        assert r.status_code == 500
        r = await client.post(
            "/api/v1/stock-quant-packages",
            json={"name": "PACK1", "package_type_id": 1, "shipping_weight": 1, "picking_id": 1},
        )
        assert r.status_code == 500

        r = await client.get("/api/v1/res-partners")
        assert r.status_code == 500
        r = await client.get("/api/v1/stock-pickings")
        assert r.status_code == 500
        r = await client.get("/api/v1/stock-package-types")
        assert r.status_code == 500
        r = await client.get("/api/v1/stock-quant-packages")
        assert r.status_code == 500
