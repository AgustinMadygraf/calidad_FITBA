from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.dtos.stock_picking_dto import StockPickingDTO
from application.use_cases._mappers import to_picking_dto
from application.exceptions import NotFoundError


class GetStockPickingById:
    def __init__(self, repo: IStockPickingRepository) -> None:
        self.repo = repo

    def execute(self, picking_id: int) -> StockPickingDTO:
        picking = self.repo.get_by_id(picking_id)
        if not picking:
            raise NotFoundError("Picking no encontrado")
        return to_picking_dto(picking)
