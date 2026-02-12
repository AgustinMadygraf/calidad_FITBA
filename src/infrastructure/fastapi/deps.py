from typing import Protocol

from ...infrastructure.httpx.categoria_fiscal_gateway_xubio import (
    XubioCategoriaFiscalGateway,
)
from ...infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from ...infrastructure.httpx.remito_gateway_xubio import XubioRemitoGateway
from ...infrastructure.httpx.producto_gateway_xubio import (
    ProductoGatewayConfig,
    XubioProductoGateway,
)
from ...infrastructure.httpx.deposito_gateway_xubio import XubioDepositoGateway
from ...infrastructure.httpx.identificacion_tributaria_gateway_xubio import (
    XubioIdentificacionTributariaGateway,
)
from ...infrastructure.httpx.lista_precio_gateway_xubio import (
    XubioListaPrecioGateway,
)
from ...infrastructure.httpx.moneda_gateway_xubio import XubioMonedaGateway
from ...infrastructure.httpx.token_gateway_httpx import HttpxTokenGateway
from ...shared.config import is_prod
from ...shared.logger import get_logger

logger = get_logger(__name__)


class Dependencies(Protocol):  # pylint: disable=too-few-public-methods
    categoria_fiscal_gateway: object
    cliente_gateway: object
    producto_gateway: object
    producto_compra_gateway: object
    deposito_gateway: object
    identificacion_tributaria_gateway: object
    lista_precio_gateway: object
    moneda_gateway: object
    token_gateway: object


def _get_read_cache_enabled() -> bool:
    return not is_prod()


def get_cliente_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioClienteGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Cliente gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_categoria_fiscal_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioCategoriaFiscalGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Categoria fiscal gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_token_gateway():
    return HttpxTokenGateway()


def get_remito_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioRemitoGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Remito gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_producto_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioProductoGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Producto gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_producto_compra_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioProductoGateway(
        config=ProductoGatewayConfig(primary_bean="ProductoCompraBean", fallback_bean=None),
        enable_get_cache=cache_enabled,
    )
    logger.info(
        "Producto compra gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_deposito_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioDepositoGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Deposito gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_identificacion_tributaria_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioIdentificacionTributariaGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Identificacion tributaria gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_lista_precio_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioListaPrecioGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Lista precio gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw


def get_moneda_gateway():
    cache_enabled = _get_read_cache_enabled()
    gw = XubioMonedaGateway(enable_get_cache=cache_enabled)
    logger.info(
        "Moneda gateway: %s (read cache enabled=%s)",
        gw.__class__.__name__,
        cache_enabled,
    )
    return gw
