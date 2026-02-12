from typing import Any, Dict, List, Optional, Protocol


class VendedorGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, vendedor_id: int) -> Optional[Dict[str, Any]]: ...
