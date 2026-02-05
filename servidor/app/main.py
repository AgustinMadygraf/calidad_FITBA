import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from dotenv import load_dotenv
from application.ports.unit_of_work import IUnitOfWork
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from infrastructure.db.unit_of_work import MySQLUnitOfWork
from servidor.app.routers.res_partners import router as res_partners_router
from servidor.app.routers.stock_pickings import router as stock_pickings_router
from servidor.app.routers.stock_package_types import router as stock_package_types_router
from servidor.app.routers.stock_quant_packages import router as stock_quant_packages_router


load_dotenv()
conn_factory = MySQLConnectionFactory.from_env()


def uow_factory() -> IUnitOfWork:
    return MySQLUnitOfWork(conn_factory)


def create_app() -> FastAPI:
    app = FastAPI(title="Odoo-like API", version="1.0.0")

    @app.on_event("startup")
    def _ensure_schema() -> None:
        schema_path = BASE_DIR / "scripts" / "schema.sql"
        conn_factory.ensure_schema(schema_path)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(res_partners_router)
    app.include_router(stock_pickings_router)
    app.include_router(stock_package_types_router)
    app.include_router(stock_quant_packages_router)
    return app


app = create_app()
