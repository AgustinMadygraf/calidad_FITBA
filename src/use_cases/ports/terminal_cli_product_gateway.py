from typing import Any, Dict, Protocol

from ..terminal_cli import PostResult


class TerminalCliProductGateway(Protocol):
    def create_product(
        self,
        base_url: str,
        payload: Dict[str, Any],
        timeout: float,
    ) -> PostResult: ...
