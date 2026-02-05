from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.exceptions import NotFoundError


class DeleteStockQuantPackage:
    def __init__(self, repo: IStockQuantPackageRepository) -> None:
        self.repo = repo

    def execute(self, package_id: int) -> None:
        existing = self.repo.get_by_id(package_id)
        if not existing:
            raise NotFoundError("Paquete no encontrado")
        self.repo.delete(package_id)
