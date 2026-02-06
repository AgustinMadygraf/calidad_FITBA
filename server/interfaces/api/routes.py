from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from shared.schemas import TerminalExecuteRequest, TerminalExecuteResponse, ProductCreate, ProductUpdate
from server.app.deps import get_db, get_xubio_client
from server.app.settings import settings
from server.infrastructure.clients.mock_xubio_api_client import MockXubioApiClient
from server.infrastructure.clients.real_xubio_api_client import RealXubioApiClient
from server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from server.interfaces.terminal import execute_command
from server.application.use_cases import SyncPullProduct

router = APIRouter()


class XubioProductPayload(BaseModel):
    productoid: str | int | None = None
    nombre: str | None = None
    codigo: str | None = None
    precioVenta: float | None = None
    name: str | None = None
    sku: str | None = None
    price: float | None = None


def _map_to_xubio(dto) -> dict[str, Any]:
    return {
        "productoid": dto.external_id,
        "nombre": dto.name,
        "codigo": dto.sku,
        "precioVenta": dto.price,
    }


def _to_product_create(payload: XubioProductPayload) -> ProductCreate:
    name = payload.nombre or payload.name
    if not name:
        raise HTTPException(status_code=422, detail="Falta nombre.")
    external_id = str(payload.productoid) if payload.productoid is not None else None
    return ProductCreate(
        external_id=external_id,
        name=name,
        sku=payload.codigo or payload.sku,
        price=payload.precioVenta if payload.precioVenta is not None else payload.price,
    )


def _to_product_update(payload: XubioProductPayload) -> ProductUpdate:
    return ProductUpdate(
        name=payload.nombre or payload.name,
        sku=payload.codigo or payload.sku,
        price=payload.precioVenta if payload.precioVenta is not None else payload.price,
    )


def _local_product_client(db: Session) -> MockXubioApiClient:
    repository = IntegrationRecordRepository(db)
    return MockXubioApiClient(repository)


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sync/pull/product/from-xubio")
def sync_pull_product_from_xubio(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    repository = IntegrationRecordRepository(db)
    result = SyncPullProduct(RealXubioApiClient(), repository).execute(False)
    if result.get("status") != "ok":
        raise HTTPException(status_code=502, detail=result.get("detail", "Error de sync pull."))
    return {"status": "ok", "source": "xubio"}


@router.get("/API/1.1/ProductoVentaBean")
def xubio_list_products(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    client = _local_product_client(db)
    items = client.list_products(limit=1000, offset=0)
    return [_map_to_xubio(item) for item in items]


@router.get("/API/1.1/ProductoVentaBean/{external_id}")
def xubio_get_product(external_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    client = _local_product_client(db)
    try:
        item = client.get_product(external_id)
        return _map_to_xubio(item)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/API/1.1/ProductoVentaBean")
def xubio_create_product(payload: XubioProductPayload, db: Session = Depends(get_db)) -> dict[str, Any]:
    client = _local_product_client(db)
    dto = client.create_product(_to_product_create(payload))
    return _map_to_xubio(dto)


@router.patch("/API/1.1/ProductoVentaBean/{external_id}")
def xubio_update_product(
    external_id: str,
    payload: XubioProductPayload,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    client = _local_product_client(db)
    try:
        dto = client.update_product(external_id, _to_product_update(payload))
        return _map_to_xubio(dto)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/API/1.1/ProductoVentaBean/{external_id}", status_code=204)
def xubio_delete_product(external_id: str, db: Session = Depends(get_db)) -> None:
    client = _local_product_client(db)
    try:
        client.delete_product(external_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/terminal/execute", response_model=TerminalExecuteResponse)
def terminal_execute(
    payload: TerminalExecuteRequest,
    db: Session = Depends(get_db),
) -> TerminalExecuteResponse:
    client = get_xubio_client(db)
    repository = IntegrationRecordRepository(db)
    session_id = payload.session_id or "default"
    session_id, screen, next_actions = execute_command(
        session_id=session_id,
        command=payload.command,
        args=payload.args,
        client=client,
        repository=repository,
    )
    return TerminalExecuteResponse(session_id=session_id, screen=screen, next_actions=next_actions)


@router.post("/sync/pull/product")
def sync_pull_product(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_xubio_client(db)
    repository = IntegrationRecordRepository(db)
    return SyncPullProduct(client, repository).execute(not settings.IS_PROD)


@router.post("/sync/push/product")
def sync_push_product(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_xubio_client(db)
    repository = IntegrationRecordRepository(db)
    records = list(repository.list(entity_type="product", status="local", limit=100, offset=0))
    if not settings.IS_PROD:
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
