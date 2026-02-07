from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy.exc import ProgrammingError

from src.entities.schemas import TerminalExecuteRequest, TerminalExecuteResponse, ProductCreate, ProductUpdate
from src.interface_adapter.controller.api.app.deps import get_db, get_xubio_client
from src.interface_adapter.controller.api.app.settings import settings
from src.interface_adapter.gateways.mock_xubio_api_client import MockXubioApiClient
from src.interface_adapter.gateways.real_xubio_api_client import RealXubioApiClient
from src.interface_adapter.presenters.product_presenter import to_xubio as present_product_to_xubio
from src.shared.logger import get_logger
from src.infrastructure.repositories.integration_record_repository import (
    ProductRepository,
)
from src.interface_adapter.controller.terminal import execute_command
from src.use_case.use_cases import SyncPullProduct

router = APIRouter()
logger = get_logger(__name__)


class XubioUnidadMedida(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    ID: int | None = None


class XubioTasaIva(BaseModel):
    codigo: str | None = None
    nombre: str | None = None
    tasaDefault: float | None = None
    porcentaje: float | None = None
    ID: int | None = None


class XubioCuentaContable(BaseModel):
    ID: int | None = None
    nombre: str | None = None
    codigo: str | None = None
    id: int | None = None


class XubioActividadEconomica(BaseModel):
    ID: int | None = None
    nombre: str | None = None
    codigo: str | None = None
    id: int | None = None


class ProductoVentaBean(BaseModel):
    model_config = ConfigDict(extra="allow")

    productoid: str | int | None = None
    nombre: str | None = None
    codigo: str | None = None
    usrcode: str | None = None
    codigoBarra: str | None = None
    unidadMedida: XubioUnidadMedida | None = None
    categoria: int | None = None
    stockNegativo: bool | None = None
    tasaIva: XubioTasaIva | None = None
    cuentaContable: XubioCuentaContable | None = None
    catFormIVA2002: int | None = None
    precioUltCompra: float | None = None
    precioVenta: float | None = None
    activo: int | bool | None = None
    actividadEconomica: XubioActividadEconomica | None = None
    sincronizaStock: int | bool | None = None
    noObjetoImpuesto: int | bool | None = None
    tipoOperacionIvaSimple: int | None = None


def _map_to_xubio(dto) -> dict[str, Any]:
    return present_product_to_xubio(dto)


def _to_product_create(payload: ProductoVentaBean) -> ProductCreate:
    name = payload.nombre
    if not name:
        raise HTTPException(status_code=422, detail="Falta nombre.")
    external_id = str(payload.productoid) if payload.productoid is not None else None
    price = payload.precioVenta if payload.precioVenta is not None else payload.precioUltCompra
    return ProductCreate(
        external_id=external_id,
        name=name,
        sku=payload.codigo,
        price=price,
        xubio_payload=payload.model_dump(exclude_none=True),
    )


def _to_product_update(payload: ProductoVentaBean) -> ProductUpdate:
    return ProductUpdate(
        name=payload.nombre,
        sku=payload.codigo,
        price=payload.precioVenta if payload.precioVenta is not None else payload.precioUltCompra,
        xubio_payload=payload.model_dump(exclude_none=True),
    )


def _local_product_client(db: Session) -> MockXubioApiClient:
    repository = ProductRepository(db)
    return MockXubioApiClient(repository)


def _to_product_create_from_payload(payload: dict[str, Any], external_id: str | None) -> ProductCreate:
    name = payload.get("name") or payload.get("nombre")
    if not name:
        raise ValueError("Falta nombre.")
    sku = payload.get("sku") or payload.get("codigo")
    price = payload.get("price")
    if price is None:
        price = payload.get("precioVenta") if payload.get("precioVenta") is not None else payload.get("precioUltCompra")
    ext = external_id or payload.get("external_id") or payload.get("productoid")
    ext_str = str(ext) if ext is not None else None
    return ProductCreate(
        external_id=ext_str,
        name=name,
        sku=sku,
        price=price,
        xubio_payload=payload,
    )


def _to_product_update_from_payload(payload: dict[str, Any]) -> ProductUpdate:
    name = payload.get("name") or payload.get("nombre")
    sku = payload.get("sku") or payload.get("codigo")
    price = payload.get("price")
    if price is None:
        price = payload.get("precioVenta") if payload.get("precioVenta") is not None else payload.get("precioUltCompra")
    return ProductUpdate(
        name=name,
        sku=sku,
        price=price,
        xubio_payload=payload,
    )


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/sync/pull/product/from-xubio")
def sync_pull_product_from_xubio(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    repository = ProductRepository(db)
    logger.info("Sync pull from Xubio started.")
    result = SyncPullProduct(RealXubioApiClient(), repository).execute(False)
    if result.get("status") != "ok":
        logger.error("Sync pull from Xubio failed: %s", result.get("detail", "Error de sync pull."))
        raise HTTPException(status_code=502, detail=result.get("detail", "Error de sync pull."))
    logger.info("Sync pull from Xubio completed.")
    return {"status": "ok", "source": "xubio"}


@router.get("/API/1.1/ProductoVentaBean")
def xubio_list_products(db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    client = _local_product_client(db)
    try:
        items = client.list_products(limit=1000, offset=0)
        return [_map_to_xubio(item) for item in items]
    except ProgrammingError as exc:
        logger.warning("DB no inicializada (tabla integration_records inexistente).")
        logger.error("Detalle DB error: %s", exc)
        raise HTTPException(status_code=500, detail="DB no inicializada: falta tabla integration_records.") from exc
    except Exception as exc:  # pylint: disable=broad-exception-caught
        logger.error("Error listando productos: %s", exc)
        raise HTTPException(status_code=500, detail="Error interno listando productos.") from exc


@router.get("/API/1.1/ProductoVentaBean/{external_id}")
def xubio_get_product(external_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    client = _local_product_client(db)
    try:
        item = client.get_product(external_id)
        return _map_to_xubio(item)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/API/1.1/ProductoVentaBean")
def xubio_create_product(payload: ProductoVentaBean, db: Session = Depends(get_db)) -> dict[str, Any]:
    client = _local_product_client(db)
    dto = client.create_product(_to_product_create(payload))
    return _map_to_xubio(dto)


@router.patch("/API/1.1/ProductoVentaBean/{external_id}")
def xubio_update_product(
    external_id: str,
    payload: ProductoVentaBean,
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
    repository = ProductRepository(db)
    session_id = payload.session_id or "default"
    logger.info("Terminal execute: session=%s command=%s", session_id, payload.command)
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
    repository = ProductRepository(db)
    logger.info("Sync pull started (is_prod=%s).", settings.IS_PROD)
    return SyncPullProduct(client, repository).execute(not settings.IS_PROD)


@router.post("/sync/push/product")
def sync_push_product(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    client = get_xubio_client(db)
    repository = ProductRepository(db)
    products = list(repository.list(limit=100, offset=0))
    if not settings.IS_PROD:
        logger.info("Sync push in mock mode: %d products skipped.", len(products))
        return {"status": "ok"}

    for product in products:
        external_id = None
        try:
            payload = repository.to_payload(product)
            external_id = repository.external_id_of(product)
            if not payload.get("nombre"):
                logger.warning("Producto %s sin nombre, se omite en sync push.", external_id)
                continue
            if external_id:
                dto = client.update_product(external_id, _to_product_update_from_payload(payload))
            else:
                dto = client.create_product(_to_product_create_from_payload(payload, None))
        except Exception as exc:  # pylint: disable=broad-exception-caught
            logger.error("Sync push failed for product %s: %s", external_id, exc)
    logger.info("Sync push completed (products=%d).", len(products))
    return {"status": "ok"}
