from typing import Any, Dict

from ...use_cases.ports.token_gateway import TokenGateway
from .token_client import get_token_status


class HttpxTokenGateway(TokenGateway):  # pylint: disable=too-few-public-methods
    def get_status(self) -> Dict[str, Any]:
        return get_token_status()
