from pymysql.connections import Connection
from pymysql.err import IntegrityError, ProgrammingError, OperationalError
from domain.entities.stock_package_type import StockPackageType
from domain.repositories.stock_package_type_repository import IStockPackageTypeRepository
from application.exceptions import DatabaseError


class MySQLStockPackageTypeRepository(IStockPackageTypeRepository):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, package_type: StockPackageType) -> StockPackageType:
        sql = "INSERT INTO stock_package_type (name, weight) VALUES (%s, %s)"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (package_type.name, package_type.weight))
                package_type.id = cur.lastrowid
            return package_type
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def update(self, package_type: StockPackageType) -> StockPackageType:
        sql = "UPDATE stock_package_type SET name=%s, weight=%s WHERE id=%s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (package_type.name, package_type.weight, package_type.id))
            return package_type
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def delete(self, package_type_id: int) -> None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM stock_package_type WHERE id=%s", (package_type_id,))
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def get_by_id(self, package_type_id: int) -> StockPackageType | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM stock_package_type WHERE id=%s", (package_type_id,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_package_type(row) if row else None

    def list(self, limit: int, offset: int) -> list[StockPackageType]:
        sql = "SELECT * FROM stock_package_type ORDER BY id DESC LIMIT %s OFFSET %s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_package_type(r) for r in rows]

    def _row_to_package_type(self, row: dict) -> StockPackageType:
        return StockPackageType(
            id=row["id"],
            name=row["name"],
            weight=float(row["weight"]),
        )

    def _raise_db_error(self, exc: Exception) -> None:
        if isinstance(exc, ProgrammingError) and exc.args and exc.args[0] == 1146:
            raise DatabaseError(
                "Tabla 'stock_package_type' no existe. Ejecuta servidor/scripts/schema.sql en la base configurada."
            ) from exc
        raise DatabaseError("Error de base de datos") from exc
