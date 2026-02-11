from typing import Any, Dict, Protocol


class TokenGateway(Protocol):
    def get_status(self) -> Dict[str, Any]: ...
