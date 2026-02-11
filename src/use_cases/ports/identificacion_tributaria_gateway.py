from typing import Any, Dict, List, Optional, Protocol


class IdentificacionTributariaGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, identificacion_tributaria_id: int) -> Optional[Dict[str, Any]]: ...
