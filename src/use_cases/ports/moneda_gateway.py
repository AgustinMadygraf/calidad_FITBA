from typing import Any, Dict, List, Optional, Protocol


class MonedaGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, moneda_id: int) -> Optional[Dict[str, Any]]: ...
