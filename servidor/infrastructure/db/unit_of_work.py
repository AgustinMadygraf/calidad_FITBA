from pymysql.connections import Connection
from application.ports.unit_of_work import IUnitOfWork
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from infrastructure.repositories.mysql_contact_repository import MySQLContactRepository


class MySQLUnitOfWork(IUnitOfWork):
    def __init__(self, conn_factory: MySQLConnectionFactory) -> None:
        self.conn_factory = conn_factory
        self.connection: Connection | None = None
        self.contacts: MySQLContactRepository | None = None

    def __enter__(self) -> "MySQLUnitOfWork":
        self.connection = self.conn_factory.connect()
        self.contacts = MySQLContactRepository(self.connection)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if not self.connection:
            return
        if exc_type:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.close()
