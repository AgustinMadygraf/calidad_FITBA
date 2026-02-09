from typing import Protocol

from ...infrastructure.httpx.cliente_gateway_xubio import XubioClienteGateway
from ...infrastructure.httpx.remito_gateway_xubio import XubioRemitoGateway
from ...infrastructure.httpx.token_gateway_httpx import HttpxTokenGateway
from ...infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway
from ...infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway
from ...shared.config import is_prod
from ...shared.logger import get_logger

logger = get_logger(__name__)


class Dependencies(Protocol):
    cliente_gateway: object
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
