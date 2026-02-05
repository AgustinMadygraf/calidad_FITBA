from infrastructure.repositories.in_memory_stock_picking_repository import InMemoryStockPickingRepository
from infrastructure.repositories.in_memory_stock_package_type_repository import InMemoryStockPackageTypeRepository
from infrastructure.repositories.in_memory_stock_quant_package_repository import InMemoryStockQuantPackageRepository
from application.use_cases.create_stock_picking import CreateStockPicking
from application.use_cases.update_stock_picking import UpdateStockPicking
from application.use_cases.delete_stock_picking import DeleteStockPicking
from application.use_cases.get_stock_picking_by_id import GetStockPickingById
from application.use_cases.list_stock_pickings import ListStockPickings
from application.use_cases.create_stock_package_type import CreateStockPackageType
from application.use_cases.update_stock_package_type import UpdateStockPackageType
from application.use_cases.delete_stock_package_type import DeleteStockPackageType
from application.use_cases.get_stock_package_type_by_id import GetStockPackageTypeById
from application.use_cases.list_stock_package_types import ListStockPackageTypes
from application.use_cases.create_stock_quant_package import CreateStockQuantPackage
from application.use_cases.update_stock_quant_package import UpdateStockQuantPackage
from application.use_cases.delete_stock_quant_package import DeleteStockQuantPackage
from application.use_cases.get_stock_quant_package_by_id import GetStockQuantPackageById
from application.use_cases.list_stock_quant_packages import ListStockQuantPackages
from application.exceptions import NotFoundError


def test_stock_picking_use_cases():
    repo = InMemoryStockPickingRepository()
    create_uc = CreateStockPicking(repo)
    update_uc = UpdateStockPicking(repo)
    get_uc = GetStockPickingById(repo)
    list_uc = ListStockPickings(repo)
    delete_uc = DeleteStockPicking(repo)

    created = create_uc.execute(name="OUT/0001", partner_id=1)
    updated = update_uc.execute(created.id, name="OUT/0002")
    assert updated.name == "OUT/0002"
    fetched = get_uc.execute(created.id)
    assert fetched.id == created.id
    assert list_uc.execute(limit=10, offset=0)
    delete_uc.execute(created.id)
    assert list_uc.execute(limit=10, offset=0) == []


def test_stock_package_type_use_cases():
    repo = InMemoryStockPackageTypeRepository()
    create_uc = CreateStockPackageType(repo)
    update_uc = UpdateStockPackageType(repo)
    get_uc = GetStockPackageTypeById(repo)
    list_uc = ListStockPackageTypes(repo)
    delete_uc = DeleteStockPackageType(repo)

    created = create_uc.execute(name="Caja A", weight=0.5)
    updated = update_uc.execute(created.id, weight=0.75)
    assert updated.weight == 0.75
    fetched = get_uc.execute(created.id)
    assert fetched.id == created.id
    assert list_uc.execute(limit=10, offset=0)
    delete_uc.execute(created.id)
    assert list_uc.execute(limit=10, offset=0) == []


def test_stock_quant_package_use_cases():
    repo = InMemoryStockQuantPackageRepository()
    create_uc = CreateStockQuantPackage(repo)
    update_uc = UpdateStockQuantPackage(repo)
    get_uc = GetStockQuantPackageById(repo)
    list_uc = ListStockQuantPackages(repo)
    delete_uc = DeleteStockQuantPackage(repo)

    created = create_uc.execute(
        name="PACK0001", package_type_id=1, shipping_weight=5.0, picking_id=1
    )
    updated = update_uc.execute(created.id, shipping_weight=6.5)
    assert updated.shipping_weight == 6.5
    fetched = get_uc.execute(created.id)
    assert fetched.id == created.id
    assert list_uc.execute(limit=10, offset=0)
    delete_uc.execute(created.id)
    assert list_uc.execute(limit=10, offset=0) == []


def test_stock_pickings_not_found():
    repo = InMemoryStockPickingRepository()
    get_uc = GetStockPickingById(repo)
    delete_uc = DeleteStockPicking(repo)
    try:
        get_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True
    try:
        delete_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True


def test_stock_package_types_not_found():
    repo = InMemoryStockPackageTypeRepository()
    get_uc = GetStockPackageTypeById(repo)
    delete_uc = DeleteStockPackageType(repo)
    try:
        get_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True
    try:
        delete_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True


def test_stock_quant_packages_not_found():
    repo = InMemoryStockQuantPackageRepository()
    get_uc = GetStockQuantPackageById(repo)
    delete_uc = DeleteStockQuantPackage(repo)
    try:
        get_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True
    try:
        delete_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True
