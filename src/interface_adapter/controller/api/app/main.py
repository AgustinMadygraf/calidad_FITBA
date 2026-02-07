from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine
from src.interface_adapter.controller.api.routes import router
from src.shared.logger import get_logger


@asynccontextmanager
async def _lifespan(app: FastAPI):
    _ = app
    logger = get_logger(__name__)
    logger.info("API startup: initializing database schema.")
    Base.metadata.create_all(bind=engine)
    logger.info("API startup complete.")
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="FITBA Xubio-like", lifespan=_lifespan)
    app.include_router(router)
    return app


app = create_app()
