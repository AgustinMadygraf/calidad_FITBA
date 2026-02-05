from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.dtos.stock_picking_dto import StockPickingDTO
from application.use_cases._mappers import to_picking_dto


class ListStockPickings:
    def __init__(self, repo: IStockPickingRepository) -> None:
        self.repo = repo

    def execute(self, limit: int, offset: int) -> list[StockPickingDTO]:
        pickings = self.repo.list(limit=limit, offset=offset)
        return [to_picking_dto(p) for p in pickings]
