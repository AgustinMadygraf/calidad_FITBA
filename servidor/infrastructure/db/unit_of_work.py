from pymysql.connections import Connection
from application.ports.unit_of_work import IUnitOfWork
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from infrastructure.repositories.mysql_res_partner_repository import MySQLResPartnerRepository
from infrastructure.repositories.mysql_stock_picking_repository import MySQLStockPickingRepository
from infrastructure.repositories.mysql_stock_package_type_repository import MySQLStockPackageTypeRepository
from infrastructure.repositories.mysql_stock_quant_package_repository import MySQLStockQuantPackageRepository


class MySQLUnitOfWork(IUnitOfWork):
    def __init__(self, conn_factory: MySQLConnectionFactory) -> None:
        self.conn_factory = conn_factory
        self.connection: Connection | None = None
        self.partners: MySQLResPartnerRepository | None = None
        self.pickings: MySQLStockPickingRepository | None = None
        self.package_types: MySQLStockPackageTypeRepository | None = None
        self.packages: MySQLStockQuantPackageRepository | None = None

    def __enter__(self) -> "MySQLUnitOfWork":
        self.connection = self.conn_factory.connect()
        self.partners = MySQLResPartnerRepository(self.connection)
        self.pickings = MySQLStockPickingRepository(self.connection)
        self.package_types = MySQLStockPackageTypeRepository(self.connection)
        self.packages = MySQLStockQuantPackageRepository(self.connection)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.connection:
            return
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
