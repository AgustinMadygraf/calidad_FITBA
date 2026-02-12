from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ..gateway_provider import gateway_provider

router = APIRouter()

CATEGORIA_FISCAL_BASE = "/API/1.1/categoriaFiscal"
CATEGORIA_FISCAL_BASE_SLASH = "/API/1.1/categoriaFiscal/"
DEPOSITO_BASE = "/API/1.1/depositos"
DEPOSITO_BASE_SLASH = "/API/1.1/depositos/"
IDENTIFICACION_TRIBUTARIA_BASE = "/API/1.1/identificacionTributaria"
IDENTIFICACION_TRIBUTARIA_BASE_SLASH = "/API/1.1/identificacionTributaria/"
MONEDA_BASE = "/API/1.1/monedaBean"
MONEDA_BASE_SLASH = "/API/1.1/monedaBean/"


@router.get(CATEGORIA_FISCAL_BASE)
@router.get(CATEGORIA_FISCAL_BASE_SLASH, include_in_schema=False)
def categoria_fiscal_list() -> Dict[str, Any]:
    return handlers.list_categorias_fiscales(
        gateway_provider.categoria_fiscal_gateway
    )


@router.get(f"{CATEGORIA_FISCAL_BASE}/{{categoria_fiscal_id}}")
@router.get(
    f"{CATEGORIA_FISCAL_BASE}/{{categoria_fiscal_id}}/", include_in_schema=False
)
def categoria_fiscal_get(categoria_fiscal_id: int) -> Dict[str, Any]:
    item = handlers.get_categoria_fiscal(
        gateway_provider.categoria_fiscal_gateway, categoria_fiscal_id
    )
    if item is None:
        raise HTTPException(status_code=404, detail="categoria fiscal no encontrada")
    return item


@router.get(DEPOSITO_BASE)
@router.get(DEPOSITO_BASE_SLASH, include_in_schema=False)
def deposito_list() -> Dict[str, Any]:
    return handlers.list_depositos(gateway_provider.deposito_gateway)


@router.get(f"{DEPOSITO_BASE}/{{deposito_id}}")
@router.get(f"{DEPOSITO_BASE}/{{deposito_id}}/", include_in_schema=False)
def deposito_get(deposito_id: int) -> Dict[str, Any]:
    item = handlers.get_deposito(gateway_provider.deposito_gateway, deposito_id)
    if item is None:
        raise HTTPException(status_code=404, detail="deposito no encontrado")
    return item


@router.get(IDENTIFICACION_TRIBUTARIA_BASE)
@router.get(IDENTIFICACION_TRIBUTARIA_BASE_SLASH, include_in_schema=False)
def identificacion_tributaria_list() -> Dict[str, Any]:
    return handlers.list_identificaciones_tributarias(
        gateway_provider.identificacion_tributaria_gateway
    )


@router.get(f"{IDENTIFICACION_TRIBUTARIA_BASE}/{{identificacion_tributaria_id}}")
@router.get(
    f"{IDENTIFICACION_TRIBUTARIA_BASE}/{{identificacion_tributaria_id}}/",
    include_in_schema=False,
)
def identificacion_tributaria_get(identificacion_tributaria_id: int) -> Dict[str, Any]:
    item = handlers.get_identificacion_tributaria(
        gateway_provider.identificacion_tributaria_gateway,
        identificacion_tributaria_id,
    )
    if item is None:
        raise HTTPException(
            status_code=404, detail="identificacion tributaria no encontrada"
        )
    return item


@router.get(MONEDA_BASE)
@router.get(MONEDA_BASE_SLASH, include_in_schema=False)
def moneda_list() -> Dict[str, Any]:
    return handlers.list_monedas(gateway_provider.moneda_gateway)


@router.get(f"{MONEDA_BASE}/{{moneda_id}}")
@router.get(f"{MONEDA_BASE}/{{moneda_id}}/", include_in_schema=False)
def moneda_get(moneda_id: int) -> Dict[str, Any]:
    item = handlers.get_moneda(gateway_provider.moneda_gateway, moneda_id)
    if item is None:
        raise HTTPException(status_code=404, detail="moneda no encontrada")
    return item
