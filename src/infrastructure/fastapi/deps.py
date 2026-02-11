from typing import Protocol

from ...infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from ...infrastructure.httpx.remito_gateway_xubio import XubioRemitoGateway
from ...infrastructure.httpx.producto_gateway_xubio import XubioProductoGateway
from ...infrastructure.httpx.deposito_gateway_xubio import XubioDepositoGateway
from ...infrastructure.httpx.token_gateway_httpx import HttpxTokenGateway
from ...infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from ...infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway
from ...infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway
from ...infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from ...shared.config import is_prod
from ...shared.logger import get_logger

logger = get_logger(__name__)


class Dependencies(Protocol):
    cliente_gateway: object
    producto_gateway: object
    producto_compra_gateway: object
    deposito_gateway: object
    token_gateway: object


def get_cliente_gateway():
    gw = XubioClienteGateway() if is_prod() else InMemoryClienteGateway()
    logger.info("Cliente gateway: %s", gw.__class__.__name__)
    return gw


def get_token_gateway():
    return HttpxTokenGateway()


def get_remito_gateway():
    gw = XubioRemitoGateway() if is_prod() else InMemoryRemitoGateway()
    logger.info("Remito gateway: %s", gw.__class__.__name__)
    return gw


def get_producto_gateway():
    gw = XubioProductoGateway() if is_prod() else InMemoryProductoGateway()
    logger.info("Producto gateway: %s", gw.__class__.__name__)
    return gw


def get_producto_compra_gateway():
    if is_prod():
        gw = XubioProductoGateway(primary_bean="ProductoCompraBean", fallback_bean=None)
    else:
        gw = InMemoryProductoGateway()
    logger.info("Producto compra gateway: %s", gw.__class__.__name__)
    return gw


def get_deposito_gateway():
    gw = XubioDepositoGateway() if is_prod() else InMemoryDepositoGateway()
    logger.info("Deposito gateway: %s", gw.__class__.__name__)
    return gw
