from domain.entities.stock_picking import StockPicking
from domain.repositories.stock_picking_repository import IStockPickingRepository


class InMemoryStockPickingRepository(IStockPickingRepository):
    def __init__(self) -> None:
        self._items: dict[int, StockPicking] = {}
        self._next_id = 1

    def create(self, picking: StockPicking) -> StockPicking:
        picking.id = self._next_id
        self._next_id += 1
        self._items[picking.id] = picking
        return picking

    def update(self, picking: StockPicking) -> StockPicking:
        self._items[picking.id] = picking
        return picking

    def delete(self, picking_id: int) -> None:
        self._items.pop(picking_id, None)

    def get_by_id(self, picking_id: int) -> StockPicking | None:
        return self._items.get(picking_id)

    def list(self, limit: int, offset: int) -> list[StockPicking]:
        items = list(self._items.values())
        return items[offset : offset + limit]
