from typing import Any, Dict

from .ports.terminal_cli_product_gateway import TerminalCliProductGateway
from .terminal_cli import PostResult


def create_product(
    gateway: TerminalCliProductGateway,
    *,
    base_url: str,
    payload: Dict[str, Any],
    timeout: float,
) -> PostResult:
    return gateway.create_product(
        base_url=base_url,
        payload=payload,
        timeout=timeout,
    )
