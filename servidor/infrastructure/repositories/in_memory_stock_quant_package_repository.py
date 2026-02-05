from domain.entities.stock_quant_package import StockQuantPackage
from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository


class InMemoryStockQuantPackageRepository(IStockQuantPackageRepository):
    def __init__(self) -> None:
        self._items: dict[int, StockQuantPackage] = {}
        self._next_id = 1

    def create(self, package: StockQuantPackage) -> StockQuantPackage:
        package.id = self._next_id
        self._next_id += 1
        self._items[package.id] = package
        return package

    def update(self, package: StockQuantPackage) -> StockQuantPackage:
        self._items[package.id] = package
        return package

    def delete(self, package_id: int) -> None:
        self._items.pop(package_id, None)

    def get_by_id(self, package_id: int) -> StockQuantPackage | None:
        return self._items.get(package_id)

    def get_by_name(self, name: str) -> StockQuantPackage | None:
        for item in self._items.values():
            if item.name == name:
                return item
        return None

    def list(self, limit: int, offset: int) -> list[StockQuantPackage]:
        items = list(self._items.values())
        return items[offset : offset + limit]
