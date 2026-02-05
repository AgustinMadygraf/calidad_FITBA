from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.dtos.stock_package_type_dto import StockPackageTypeDTO
from application.use_cases._mappers import to_package_type_dto
from application.exceptions import NotFoundError


class GetStockPackageTypeById:
    def __init__(self, repo: IStockPackageTypeRepository) -> None:
        self.repo = repo

    def execute(self, package_type_id: int) -> StockPackageTypeDTO:
        package_type = self.repo.get_by_id(package_type_id)
        if not package_type:
            raise NotFoundError("Tipo de paquete no encontrado")
        return to_package_type_dto(package_type)
