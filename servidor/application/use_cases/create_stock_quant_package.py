from domain.entities.stock_quant_package import StockQuantPackage
from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.dtos.stock_quant_package_dto import StockQuantPackageDTO
from application.use_cases._mappers import to_quant_package_dto


class CreateStockQuantPackage:
    def __init__(self, repo: IStockQuantPackageRepository) -> None:
        self.repo = repo

    def execute(
        self,
        name: str,
        package_type_id: int,
        shipping_weight: float = 0.0,
        picking_id: int = 0,
    ) -> StockQuantPackageDTO:
        package = StockQuantPackage(
            name=name,
            package_type_id=package_type_id,
            shipping_weight=shipping_weight,
            picking_id=picking_id,
        )
        created = self.repo.create(package)
        return to_quant_package_dto(created)
