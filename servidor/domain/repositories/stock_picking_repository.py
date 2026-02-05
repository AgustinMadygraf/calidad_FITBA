from abc import ABC, abstractmethod
from domain.entities.stock_picking import StockPicking


class IStockPickingRepository(ABC):
    @abstractmethod
    def create(self, picking: StockPicking) -> StockPicking: ...

    @abstractmethod
    def update(self, picking: StockPicking) -> StockPicking: ...

    @abstractmethod
    def delete(self, picking_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, picking_id: int) -> StockPicking | None: ...

    @abstractmethod
    def list(self, limit: int, offset: int) -> list[StockPicking]: ...
