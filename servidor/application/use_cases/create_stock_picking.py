from domain.entities.stock_picking import StockPicking
from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.dtos.stock_picking_dto import StockPickingDTO
from application.use_cases._mappers import to_picking_dto


class CreateStockPicking:
    def __init__(self, repo: IStockPickingRepository) -> None:
        self.repo = repo

    def execute(self, name: str, partner_id: int) -> StockPickingDTO:
        picking = StockPicking(name=name, partner_id=partner_id)
        created = self.repo.create(picking)
        return to_picking_dto(created)
