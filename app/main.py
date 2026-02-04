from pathlib import Path
from dotenv import load_dotenv
from presentation.cli.menu import main_menu
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from application.ports.unit_of_work import IUnitOfWork
from infrastructure.db.unit_of_work import MySQLUnitOfWork


def run() -> None:
    load_dotenv()
    conn_factory = MySQLConnectionFactory.from_env()
    schema_path = Path(__file__).resolve().parents[1] / "scripts" / "schema.sql"
    try:
        conn_factory.ensure_schema(schema_path)
    except Exception as exc:
        print(f"Error al inicializar esquema: {exc}")
        return

    def uow_factory() -> IUnitOfWork:
        return MySQLUnitOfWork(conn_factory)

    main_menu(uow_factory)
