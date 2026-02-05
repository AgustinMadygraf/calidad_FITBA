from domain.entities.stock_package_type import StockPackageType
from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.dtos.stock_package_type_dto import StockPackageTypeDTO
from application.use_cases._mappers import to_package_type_dto


class CreateStockPackageType:
    def __init__(self, repo: IStockPackageTypeRepository) -> None:
        self.repo = repo

    def execute(self, name: str, weight: float = 0.0) -> StockPackageTypeDTO:
        package_type = StockPackageType(name=name, weight=weight)
        created = self.repo.create(package_type)
        return to_package_type_dto(created)
