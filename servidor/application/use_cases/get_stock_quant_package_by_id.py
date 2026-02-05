from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.dtos.stock_quant_package_dto import StockQuantPackageDTO
from application.use_cases._mappers import to_quant_package_dto
from application.exceptions import NotFoundError


class GetStockQuantPackageById:
    def __init__(self, repo: IStockQuantPackageRepository) -> None:
        self.repo = repo

    def execute(self, package_id: int) -> StockQuantPackageDTO:
        package = self.repo.get_by_id(package_id)
        if not package:
            raise NotFoundError("Paquete no encontrado")
        return to_quant_package_dto(package)
