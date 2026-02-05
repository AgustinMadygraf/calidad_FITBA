from __future__ import annotations

from fastapi import FastAPI

from server.infrastructure.db.models import Base
from server.infrastructure.db.session import engine
from server.interfaces.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="FITBA Xubio-like")
    app.include_router(router)
    return app


app = create_app()


@app.on_event("startup")
def _startup() -> None:
    Base.metadata.create_all(bind=engine)
