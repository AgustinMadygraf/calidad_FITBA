from typing import Any, Dict, List, Optional, Protocol


class ComprobanteVentaGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, comprobante_id: int) -> Optional[Dict[str, Any]]: ...
