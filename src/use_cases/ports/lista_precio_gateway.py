from typing import Any, Dict, List, Optional, Protocol


class ListaPrecioGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, lista_precio_id: int) -> Optional[Dict[str, Any]]: ...
