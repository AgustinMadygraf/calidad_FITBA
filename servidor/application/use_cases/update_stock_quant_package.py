from domain.entities.stock_quant_package import StockQuantPackage
from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.dtos.stock_quant_package_dto import StockQuantPackageDTO
from application.use_cases._mappers import to_quant_package_dto
from application.exceptions import NotFoundError


class UpdateStockQuantPackage:
    def __init__(self, repo: IStockQuantPackageRepository) -> None:
        self.repo = repo

    def execute(
        self,
        package_id: int,
        name: str | None = None,
        package_type_id: int | None = None,
        shipping_weight: float | None = None,
        picking_id: int | None = None,
    ) -> StockQuantPackageDTO:
        existing = self.repo.get_by_id(package_id)
        if not existing:
            raise NotFoundError("Paquete no encontrado")
        package = StockQuantPackage(
            id=package_id,
            name=name if name is not None else existing.name,
            package_type_id=package_type_id if package_type_id is not None else existing.package_type_id,
            shipping_weight=shipping_weight if shipping_weight is not None else existing.shipping_weight,
            picking_id=picking_id if picking_id is not None else existing.picking_id,
        )
        updated = self.repo.update(package)
        return to_quant_package_dto(updated)
