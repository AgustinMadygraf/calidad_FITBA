from domain.entities.stock_package_type import StockPackageType
from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.dtos.stock_package_type_dto import StockPackageTypeDTO
from application.use_cases._mappers import to_package_type_dto
from application.exceptions import NotFoundError


class UpdateStockPackageType:
    def __init__(self, repo: IStockPackageTypeRepository) -> None:
        self.repo = repo

    def execute(self, package_type_id: int, name: str | None = None, weight: float | None = None) -> StockPackageTypeDTO:
        existing = self.repo.get_by_id(package_type_id)
        if not existing:
            raise NotFoundError("Tipo de paquete no encontrado")
        package_type = StockPackageType(
            id=package_type_id,
            name=name if name is not None else existing.name,
            weight=weight if weight is not None else existing.weight,
        )
        updated = self.repo.update(package_type)
        return to_package_type_dto(updated)
