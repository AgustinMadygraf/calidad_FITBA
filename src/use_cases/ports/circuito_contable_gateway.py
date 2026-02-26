from typing import Any, Dict, List, Optional, Protocol


class CircuitoContableGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, circuito_contable_id: int) -> Optional[Dict[str, Any]]: ...
