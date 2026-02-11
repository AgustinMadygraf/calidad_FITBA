from typing import Any, Dict, List, Optional, Protocol


class ProductoGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]:
        ...

    def get(self, producto_id: int) -> Optional[Dict[str, Any]]:
        ...
