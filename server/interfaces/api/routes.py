from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from shared.schemas import TerminalExecuteRequest, TerminalExecuteResponse, ProductCreate, ProductUpdate
from server.app.deps import get_db, get_xubio_client
from server.app.settings import settings
from server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from server.interfaces.terminal import execute_command

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/terminal/execute", response_model=TerminalExecuteResponse)
def terminal_execute(
    payload: TerminalExecuteRequest,
    db: Session = Depends(get_db),
) -> TerminalExecuteResponse:
    client = get_xubio_client(db)
    session_id = payload.session_id or "default"
    session_id, screen, next_actions = execute_command(
        session_id=session_id,
        command=payload.command,
        args=payload.args,
        client=client,
    )
    return TerminalExecuteResponse(session_id=session_id, screen=screen, next_actions=next_actions)


@router.post("/sync/pull/product")
def sync_pull_product(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_xubio_client(db)
    if settings.xubio_mode == "mock":
        repository = IntegrationRecordRepository(db)
        if not list(repository.list(entity_type="product", limit=1, offset=0)):
            repository.create(
                entity_type="product",
                operation="create",
                external_id="demo-1",
                payload_json={"external_id": "demo-1", "name": "Producto demo"},
                status="synced",
            )
        return {"status": "ok"}

    items = client.list_products()
    repository = IntegrationRecordRepository(db)
    for item in items:
        existing = repository.get_by_external_id("product", item.external_id)
        payload = item.model_dump()
        if existing:
            repository.update(existing, operation="update", payload_json=payload, status="synced")
        else:
            repository.create(
                entity_type="product",
                operation="create",
                external_id=item.external_id,
                payload_json=payload,
                status="synced",
            )
    return {"status": "ok"}


@router.post("/sync/push/product")
def sync_push_product(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_xubio_client(db)
    repository = IntegrationRecordRepository(db)
    records = list(repository.list(entity_type="product", status="local", limit=100, offset=0))
    if settings.xubio_mode == "mock":
        for record in records:
            repository.update(record, operation=record.operation, status="synced")
        return {"status": "ok"}

    for record in records:
        try:
            payload = record.payload_json
            external_id = record.external_id
            if record.operation == "create":
                dto = client.create_product(ProductCreate(**payload))
                repository.update(record, operation="create", payload_json=dto.model_dump(), status="synced")
            elif record.operation == "update" and external_id:
                dto = client.update_product(external_id, ProductUpdate(**payload))
                repository.update(record, operation="update", payload_json=dto.model_dump(), status="synced")
            elif record.operation == "delete" and external_id:
                client.delete_product(external_id)
                repository.update(record, operation="delete", status="synced")
        except Exception as exc:
            repository.update(record, operation=record.operation, status="error", last_error=str(exc))
    return {"status": "ok"}
