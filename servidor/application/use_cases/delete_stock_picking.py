from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.exceptions import NotFoundError


class DeleteStockPicking:
    def __init__(self, repo: IStockPickingRepository) -> None:
        self.repo = repo

    def execute(self, picking_id: int) -> None:
        existing = self.repo.get_by_id(picking_id)
        if not existing:
            raise NotFoundError("Picking no encontrado")
        self.repo.delete(picking_id)
