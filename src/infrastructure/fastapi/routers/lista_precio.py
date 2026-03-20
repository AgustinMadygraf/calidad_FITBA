from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ....interface_adapter.controllers import handlers
from ....interface_adapter.schemas.lista_precio import ListaPrecioDetailResponse
from ....shared.logger import get_logger
from ..gateway_provider import gateway_provider

router = APIRouter()
logger = get_logger(__name__)

LISTA_PRECIO_BASE = "/API/1.1/listaPrecioBean"
LISTA_PRECIO_BASE_SLASH = "/API/1.1/listaPrecioBean/"
LISTA_PRECIO_DETAIL_EXAMPLE = {
    "listaPrecioID": 0,
    "activo": True,
    "nombre": "string",
    "descripcion": "string",
    "esDefault": True,
    "moneda": {
        "ID": 0,
        "nombre": "Pesos Argentinos",
        "codigo": "string",
        "id": 0,
    },
    "tipo": 0,
    "iva": 0,
    "listaReferencia": {
        "ID": 0,
        "nombre": "string",
        "codigo": "string",
        "id": 0,
    },
    "listaPrecioItem": [
        {
            "listaPrecioID": 0,
            "producto": {
                "ID": 0,
                "nombre": "Producto al 21%",
                "codigo": "string",
                "id": 0,
            },
            "precio": 0,
            "codigo": "string",
            "referencia": 0,
        }
    ],
    "ocultarSinPrecio": True,
}


@router.get(LISTA_PRECIO_BASE)
@router.get(LISTA_PRECIO_BASE_SLASH, include_in_schema=False)
def lista_precio_list() -> Dict[str, Any]:
    return handlers.list_lista_precios(gateway_provider.lista_precio_gateway)


@router.get(
    f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}",
    response_model=ListaPrecioDetailResponse,
    response_model_exclude_none=True,
    responses={
        200: {
            "description": "Detalle de lista de precio",
            "content": {"application/json": {"example": LISTA_PRECIO_DETAIL_EXAMPLE}},
        }
    },
)
@router.get(f"{LISTA_PRECIO_BASE}/{{lista_precio_id}}/", include_in_schema=False)
def lista_precio_get(lista_precio_id: int) -> ListaPrecioDetailResponse:
    item = handlers.get_lista_precio(
        gateway_provider.lista_precio_gateway, lista_precio_id
    )
    if item is None:
        raise HTTPException(status_code=404, detail="lista de precio no encontrada")
    if isinstance(item, dict):
        raw_items = item.get("listaPrecioItem")
        item_count = len(raw_items) if isinstance(raw_items, list) else 0
        logger.info(
            "ListaPrecio detalle %s: keys=%s items=%d",
            lista_precio_id,
            ",".join(sorted(item.keys())),
            item_count,
        )
    return ListaPrecioDetailResponse.model_validate(item)
