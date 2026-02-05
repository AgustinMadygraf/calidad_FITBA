from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.exceptions import NotFoundError


class DeleteStockPackageType:
    def __init__(self, repo: IStockPackageTypeRepository) -> None:
        self.repo = repo

    def execute(self, package_type_id: int) -> None:
        existing = self.repo.get_by_id(package_type_id)
        if not existing:
            raise NotFoundError("Tipo de paquete no encontrado")
        self.repo.delete(package_type_id)
