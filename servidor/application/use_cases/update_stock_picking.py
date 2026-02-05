from domain.entities.stock_picking import StockPicking
from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.dtos.stock_picking_dto import StockPickingDTO
from application.use_cases._mappers import to_picking_dto
from application.exceptions import NotFoundError


class UpdateStockPicking:
    def __init__(self, repo: IStockPickingRepository) -> None:
        self.repo = repo

    def execute(self, picking_id: int, name: str | None = None, partner_id: int | None = None) -> StockPickingDTO:
        existing = self.repo.get_by_id(picking_id)
        if not existing:
            raise NotFoundError("Picking no encontrado")
        picking = StockPicking(
            id=picking_id,
            name=name if name is not None else existing.name,
            partner_id=partner_id if partner_id is not None else existing.partner_id,
        )
        updated = self.repo.update(picking)
        return to_picking_dto(updated)
