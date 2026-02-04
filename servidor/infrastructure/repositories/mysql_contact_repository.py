from pymysql.connections import Connection
from pymysql.err import IntegrityError, ProgrammingError, OperationalError
from domain.entities.contact import Contact
from domain.repositories.contact_repository import IContactRepository
from domain.value_objects.email import Email
from domain.value_objects.phone import OptionalPhone
from domain.exceptions import DuplicateEmailError
from application.exceptions import DatabaseError


class MySQLContactRepository(IContactRepository):
    def __init__(self, connection: Connection) -> None:
        self.connection = connection

    def create(self, contact: Contact) -> Contact:
        sql = (
            "INSERT INTO contacts (full_name, email, phone, company, notes, is_customer, is_supplier) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        contact.full_name,
                        contact.email.value if contact.email else None,
                        contact.phone.value if contact.phone else None,
                        contact.company,
                        contact.notes,
                        int(contact.is_customer),
                        int(contact.is_supplier),
                    ),
                )
                contact.id = cur.lastrowid
            return contact
        except IntegrityError as exc:
            if "email" in str(exc).lower():
                raise DuplicateEmailError("Email duplicado") from exc
            raise
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def update(self, contact: Contact) -> Contact:
        sql = (
            "UPDATE contacts SET full_name=%s, email=%s, phone=%s, company=%s, notes=%s, "
            "is_customer=%s, is_supplier=%s WHERE id=%s"
        )
        try:
            with self.connection.cursor() as cur:
                cur.execute(
                    sql,
                    (
                        contact.full_name,
                        contact.email.value if contact.email else None,
                        contact.phone.value if contact.phone else None,
                        contact.company,
                        contact.notes,
                        int(contact.is_customer),
                        int(contact.is_supplier),
                        contact.id,
                    ),
                )
            return contact
        except IntegrityError as exc:
            if "email" in str(exc).lower():
                raise DuplicateEmailError("Email duplicado") from exc
            raise
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def delete(self, contact_id: int) -> None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("DELETE FROM contacts WHERE id=%s", (contact_id,))
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)

    def get_by_id(self, contact_id: int) -> Contact | None:
        try:
            with self.connection.cursor() as cur:
                cur.execute("SELECT * FROM contacts WHERE id=%s", (contact_id,))
                row = cur.fetchone()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return self._row_to_contact(row) if row else None

    def search(self, query: str, limit: int, offset: int) -> list[Contact]:
        like = f"%{query}%"
        sql = (
            "SELECT * FROM contacts WHERE full_name LIKE %s OR email LIKE %s OR phone LIKE %s "
            "ORDER BY id DESC LIMIT %s OFFSET %s"
        )
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (like, like, like, limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_contact(r) for r in rows]

    def list(self, limit: int, offset: int) -> list[Contact]:
        sql = "SELECT * FROM contacts ORDER BY id DESC LIMIT %s OFFSET %s"
        try:
            with self.connection.cursor() as cur:
                cur.execute(sql, (limit, offset))
                rows = cur.fetchall()
        except (ProgrammingError, OperationalError) as exc:
            self._raise_db_error(exc)
        return [self._row_to_contact(r) for r in rows]

    def _row_to_contact(self, row: dict) -> Contact:
        return Contact(
            id=row["id"],
            full_name=row["full_name"],
            email=Email(row["email"]) if row.get("email") else None,
            phone=OptionalPhone(row["phone"]) if row.get("phone") else None,
            company=row.get("company"),
            notes=row.get("notes"),
            is_customer=bool(row.get("is_customer")),
            is_supplier=bool(row.get("is_supplier")),
        )

    def _raise_db_error(self, exc: Exception) -> None:
        if isinstance(exc, ProgrammingError) and exc.args and exc.args[0] == 1146:
            raise DatabaseError(
                "Tabla 'contacts' no existe. Ejecutá servidor/scripts/schema.sql en la base configurada."
            ) from exc
        raise DatabaseError("Error de base de datos") from exc
