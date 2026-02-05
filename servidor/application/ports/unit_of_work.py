from abc import ABC, abstractmethod
from domain.repositories.res_partner_repository import IResPartnerRepository
from domain.repositories.stock_picking_repository import IStockPickingRepository
from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository


class IUnitOfWork(ABC):
    partners: IResPartnerRepository
    pickings: IStockPickingRepository
    package_types: IStockPackageTypeRepository
    packages: IStockQuantPackageRepository

    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...

    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None: ...
