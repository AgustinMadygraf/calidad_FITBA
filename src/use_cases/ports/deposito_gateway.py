from typing import Any, Dict, List, Optional, Protocol


class DepositoGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, deposito_id: int) -> Optional[Dict[str, Any]]: ...
