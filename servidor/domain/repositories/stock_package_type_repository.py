from abc import ABC, abstractmethod
from domain.entities.stock_package_type import StockPackageType


class IStockPackageTypeRepository(ABC):
    @abstractmethod
    def create(self, package_type: StockPackageType) -> StockPackageType: ...

    @abstractmethod
    def update(self, package_type: StockPackageType) -> StockPackageType: ...

    @abstractmethod
    def delete(self, package_type_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, package_type_id: int) -> StockPackageType | None: ...

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[StockPackageType]: ...
