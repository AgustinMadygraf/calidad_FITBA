from domain.entities.stock_package_type import StockPackageType
from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository


class InMemoryStockPackageTypeRepository(IStockPackageTypeRepository):
    def __init__(self) -> None:
        self._items: dict[int, StockPackageType] = {}
        self._next_id = 1

    def create(self, package_type: StockPackageType) -> StockPackageType:
        package_type.id = self._next_id
        self._next_id += 1
        self._items[package_type.id] = package_type
        return package_type

    def update(self, package_type: StockPackageType) -> StockPackageType:
        self._items[package_type.id] = package_type
        return package_type

    def delete(self, package_type_id: int) -> None:
        self._items.pop(package_type_id, None)

    def get_by_id(self, package_type_id: int) -> StockPackageType | None:
        return self._items.get(package_type_id)

    def list(self, limit: int, offset: int) -> list[StockPackageType]:
        items = list(self._items.values())
        return items[offset : offset + limit]
