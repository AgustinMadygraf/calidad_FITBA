from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.db.models import Base
from src.infrastructure.db.session import engine
from src.interface_adapter.controller.api.routes import router


@asynccontextmanager
async def _lifespan(app: FastAPI):
    _ = app
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="FITBA Xubio-like", lifespan=_lifespan)
    app.include_router(router)
    return app


app = create_app()
