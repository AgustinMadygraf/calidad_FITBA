from pymysql.connections import Connection
from pymysql.err import IntegrityError, ProgrammingError, OperationalError
from domain.entities.stock_picking import StockPicking
from domain.repositories.stock_picking_repository import IStockPickingRepository
from application.exceptions import DatabaseError


class MySQLStockPickingRepository(IStockPickingRepository):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, picking: StockPicking) -> StockPicking:
        sql = "INSERT INTO stock_picking (name, partner_id) VALUES (%s, %s)"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (picking.name, picking.partner_id))
                picking.id = cur.lastrowid
            return picking
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def update(self, picking: StockPicking) -> StockPicking:
        sql = "UPDATE stock_picking SET name=%s, partner_id=%s WHERE id=%s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (picking.name, picking.partner_id, picking.id))
            return picking
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def delete(self, picking_id: int) -> None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM stock_picking WHERE id=%s", (picking_id,))
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def get_by_id(self, picking_id: int) -> StockPicking | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM stock_picking WHERE id=%s", (picking_id,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_picking(row) if row else None

    def list(self, limit: int, offset: int) -> list[StockPicking]:
        sql = "SELECT * FROM stock_picking ORDER BY id DESC LIMIT %s OFFSET %s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_picking(r) for r in rows]

    def _row_to_picking(self, row: dict) -> StockPicking:
        return StockPicking(
            id=row["id"],
            name=row["name"],
            partner_id=row["partner_id"],
        )

    def _raise_db_error(self, exc: Exception) -> None:
        if isinstance(exc, ProgrammingError) and exc.args and exc.args[0] == 1146:
            raise DatabaseError(
                "Tabla 'stock_picking' no existe. Ejecuta servidor/scripts/schema.sql en la base configurada."
            ) from exc
        raise DatabaseError("Error de base de datos") from exc
