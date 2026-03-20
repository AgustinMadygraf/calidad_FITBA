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
    return PostResult(
        ok=False,
        status_code=405,
        message="Modo solo lectura: crear producto no esta permitido.",
        payload=None,
    )
