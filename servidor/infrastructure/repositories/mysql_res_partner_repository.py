from pymysql.connections import Connection
from pymysql.err import IntegrityError, ProgrammingError, OperationalError
from domain.entities.res_partner import ResPartner
from domain.repositories.res_partner_repository import IResPartnerRepository
from application.exceptions import DatabaseError


class MySQLResPartnerRepository(IResPartnerRepository):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, partner: ResPartner) -> ResPartner:
        sql = "INSERT INTO res_partner (name, email, phone) VALUES (%s, %s, %s)"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (partner.name, partner.email, partner.phone))
                partner.id = cur.lastrowid
            return partner
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def update(self, partner: ResPartner) -> ResPartner:
        sql = "UPDATE res_partner SET name=%s, email=%s, phone=%s WHERE id=%s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (partner.name, partner.email, partner.phone, partner.id))
            return partner
        except (IntegrityError, ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def delete(self, partner_id: int) -> None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM res_partner WHERE id=%s", (partner_id,))
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def get_by_id(self, partner_id: int) -> ResPartner | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM res_partner WHERE id=%s", (partner_id,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_partner(row) if row else None

    def list(self, limit: int, offset: int) -> list[ResPartner]:
        sql = "SELECT * FROM res_partner ORDER BY id DESC LIMIT %s OFFSET %s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_partner(r) for r in rows]

    def _row_to_partner(self, row: dict) -> ResPartner:
        return ResPartner(
            id=row["id"],
            name=row["name"],
            email=row.get("email"),
            phone=row.get("phone"),
        )

    def _raise_db_error(self, exc: Exception) -> None:
        if isinstance(exc, ProgrammingError) and exc.args and exc.args[0] == 1146:
            raise DatabaseError(
                "Tabla 'res_partner' no existe. Ejecuta servidor/scripts/schema.sql en la base configurada."
            ) from exc
        raise DatabaseError("Error de base de datos") from exc
