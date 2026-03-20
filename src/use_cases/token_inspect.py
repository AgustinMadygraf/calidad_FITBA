from typing import Any, Dict

from ..use_cases.ports.token_gateway import TokenGateway


def execute(gateway: TokenGateway) -> Dict[str, Any]:
    return gateway.get_status()
