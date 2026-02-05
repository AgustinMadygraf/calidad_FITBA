from abc import ABC, abstractmethod
from domain.entities.stock_quant_package import StockQuantPackage


class IStockQuantPackageRepository(ABC):
    @abstractmethod
    def create(self, package: StockQuantPackage) -> StockQuantPackage: ...

    @abstractmethod
    def update(self, package: StockQuantPackage) -> StockQuantPackage: ...

    @abstractmethod
    def delete(self, package_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, package_id: int) -> StockQuantPackage | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> StockQuantPackage | None: ...

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[StockQuantPackage]: ...
