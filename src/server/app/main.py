from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.server.infrastructure.db.models import Base
from src.server.infrastructure.db.session import engine
from src.server.interfaces.api.routes import router


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
