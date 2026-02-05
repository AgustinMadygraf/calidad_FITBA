from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.dtos.stock_quant_package_dto import StockQuantPackageDTO
from application.use_cases._mappers import to_quant_package_dto


class ListStockQuantPackages:
    def __init__(self, repo: IStockQuantPackageRepository) -> None:
        self.repo = repo

    def execute(self, limit: int, offset: int) -> list[StockQuantPackageDTO]:
        packages = self.repo.list(limit=limit, offset=offset)
        return [to_quant_package_dto(p) for p in packages]
