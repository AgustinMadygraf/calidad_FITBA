from typing import Any, Dict

from ...interface_adapter.gateways.token_gateway import TokenGateway
from .token_client import get_token_status


class HttpxTokenGateway(TokenGateway):
    def get_status(self) -> Dict[str, Any]:
        return get_token_status()
