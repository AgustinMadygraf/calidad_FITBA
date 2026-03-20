from typing import Any, Dict, Protocol


class TokenGateway(Protocol):  # pylint: disable=too-few-public-methods
    def get_status(self) -> Dict[str, Any]: ...
