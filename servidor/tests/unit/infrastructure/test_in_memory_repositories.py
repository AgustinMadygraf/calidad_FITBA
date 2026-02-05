from infrastructure.repositories.in_memory_res_partner_repository import InMemoryResPartnerRepository
from infrastructure.repositories.in_memory_stock_picking_repository import InMemoryStockPickingRepository
from infrastructure.repositories.in_memory_stock_package_type_repository import InMemoryStockPackageTypeRepository
from infrastructure.repositories.in_memory_stock_quant_package_repository import InMemoryStockQuantPackageRepository
from domain.entities.res_partner import ResPartner
from domain.entities.stock_picking import StockPicking
from domain.entities.stock_package_type import StockPackageType
from domain.entities.stock_quant_package import StockQuantPackage


def test_in_memory_res_partner_repository():
    repo = InMemoryResPartnerRepository()
    partner = ResPartner(name="Cliente A")
    created = repo.create(partner)
    assert repo.get_by_id(created.id)
    repo.delete(created.id)
    assert repo.get_by_id(created.id) is None


def test_in_memory_stock_picking_repository():
    repo = InMemoryStockPickingRepository()
    picking = StockPicking(name="OUT/0001", partner_id=1)
    created = repo.create(picking)
    assert repo.get_by_id(created.id)
    repo.delete(created.id)
    assert repo.get_by_id(created.id) is None


def test_in_memory_stock_package_type_repository():
    repo = InMemoryStockPackageTypeRepository()
    package_type = StockPackageType(name="Caja A", weight=0.5)
    created = repo.create(package_type)
    assert repo.get_by_id(created.id)
    repo.delete(created.id)
    assert repo.get_by_id(created.id) is None


def test_in_memory_stock_quant_package_repository():
    repo = InMemoryStockQuantPackageRepository()
    package = StockQuantPackage(
        name="PACK001", package_type_id=1, shipping_weight=2.5, picking_id=1
    )
    created = repo.create(package)
    assert repo.get_by_id(created.id)
    assert repo.get_by_name("PACK001")
    assert repo.get_by_name("NOPE") is None
    repo.delete(created.id)
    assert repo.get_by_id(created.id) is None
