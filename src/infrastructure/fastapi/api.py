from typing import Any, Dict, Optional

from fastapi import HTTPException
from pydantic import BaseModel

from ...interface_adapter.controllers import handlers
from ...shared.config import load_env
from ...shared.logger import get_logger
from .app import app

logger = get_logger(__name__)


class TerminalExecuteRequest(BaseModel):
    command: str


class SyncRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


load_env()


@app.get("/")
def root() -> Dict[str, str]:
    return handlers.root()


@app.get("/health")
def health() -> Dict[str, str]:
    return handlers.health()


@app.post("/terminal/execute")
def terminal_execute(body: TerminalExecuteRequest) -> Dict[str, Any]:
    logger.info("Terminal command received: %s", body.command)
    return handlers.terminal_execute(body.command)


@app.post("/sync/pull/product")
def sync_pull_product(body: SyncRequest) -> Dict[str, Any]:
    return handlers.sync_pull_product(body.payload)


@app.post("/sync/push/product")
def sync_push_product(body: SyncRequest) -> Dict[str, Any]:
    return handlers.sync_push_product(body.payload)


@app.get("/token/inspect")
def token_inspect() -> Dict[str, Any]:
    try:
        return handlers.inspect_token()
    except ValueError as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Token inspect error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


def run() -> None:
    import os
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    logger.info("Iniciando FastAPI en 0.0.0.0:%d", port)
    uvicorn.run("src.infrastructure.fastapi.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run()
