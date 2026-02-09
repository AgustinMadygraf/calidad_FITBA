from typing import Any, Dict

from ..interface_adapter.gateways.token_gateway import TokenGateway


def execute(gateway: TokenGateway) -> Dict[str, Any]:
    return gateway.get_status()
