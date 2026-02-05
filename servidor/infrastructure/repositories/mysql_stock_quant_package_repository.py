from pymysql.connections import Connection
from pymysql.err import IntegrityError, ProgrammingError, OperationalError
from domain.entities.stock_quant_package import StockQuantPackage
from domain.repositories.stock_quant_package_repository import IStockQuantPackageRepository
from application.exceptions import DatabaseError


class MySQLStockQuantPackageRepository(IStockQuantPackageRepository):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, package: StockQuantPackage) -> StockQuantPackage:
        sql = (
            "INSERT INTO stock_quant_package (name, package_type_id, shipping_weight, picking_id) "
            "VALUES (%s, %s, %s, %s)"
        )
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        package.name,
                        package.package_type_id,
                        package.shipping_weight,
                        package.picking_id,
                    ),
                )
                package.id = cur.lastrowid
            return package
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def update(self, package: StockQuantPackage) -> StockQuantPackage:
        sql = (
            "UPDATE stock_quant_package SET name=%s, package_type_id=%s, shipping_weight=%s, "
            "picking_id=%s WHERE id=%s"
        )
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        package.name,
                        package.package_type_id,
                        package.shipping_weight,
                        package.picking_id,
                        package.id,
                    ),
                )
            return package
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def delete(self, package_id: int) -> None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM stock_quant_package WHERE id=%s", (package_id,))
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def get_by_id(self, package_id: int) -> StockQuantPackage | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM stock_quant_package WHERE id=%s", (package_id,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_package(row) if row else None

    def get_by_name(self, name: str) -> StockQuantPackage | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM stock_quant_package WHERE name=%s", (name,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_package(row) if row else None

    def list(self, limit: int, offset: int) -> list[StockQuantPackage]:
        sql = "SELECT * FROM stock_quant_package ORDER BY id DESC LIMIT %s OFFSET %s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_package(r) for r in rows]

    def _row_to_package(self, row: dict) -> StockQuantPackage:
        return StockQuantPackage(
            id=row["id"],
            name=row["name"],
            package_type_id=row["package_type_id"],
            shipping_weight=float(row["shipping_weight"]),
            picking_id=row["picking_id"],
        )

    def _raise_db_error(self, exc: Exception) -> None:
        if isinstance(exc, ProgrammingError) and exc.args and exc.args[0] == 1146:
            raise DatabaseError(
                "Tabla 'stock_quant_package' no existe. Ejecuta servidor/scripts/schema.sql en la base configurada."
            ) from exc
        raise DatabaseError("Error de base de datos") from exc
