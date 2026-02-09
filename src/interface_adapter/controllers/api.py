"""
Path: src/interface_adapter/controllers/api.py
"""

import os
from typing import Any, Dict, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from ...shared.logger import get_logger

app = FastAPI(title="Xubio-like API", version="0.1.0")
logger = get_logger(__name__)


class TerminalExecuteRequest(BaseModel):
    command: str


class SyncRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/terminal/execute")
def terminal_execute(body: TerminalExecuteRequest) -> Dict[str, Any]:
    logger.info("Terminal command received: %s", body.command)
    return {"status": "stub", "echo": body.command}


@app.post("/sync/pull/product")
def sync_pull_product(body: SyncRequest) -> Dict[str, Any]:
    return {"status": "stub", "action": "pull", "entity": "product", "payload": body.payload}


@app.post("/sync/push/product")
def sync_push_product(body: SyncRequest) -> Dict[str, Any]:
    return {"status": "stub", "action": "push", "entity": "product", "payload": body.payload}


def run() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("src.interface_adapter.controllers.api:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run()
