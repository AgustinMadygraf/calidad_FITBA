from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.dtos.stock_package_type_dto import StockPackageTypeDTO
from application.use_cases._mappers import to_package_type_dto


class ListStockPackageTypes:
    def __init__(self, repo: IStockPackageTypeRepository) -> None:
        self.repo = repo

    def execute(self, limit: int, offset: int) -> list[StockPackageTypeDTO]:
        package_types = self.repo.list(limit=limit, offset=offset)
        return [to_package_type_dto(p) for p in package_types]
