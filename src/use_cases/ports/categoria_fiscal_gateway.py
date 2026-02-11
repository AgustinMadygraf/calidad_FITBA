from typing import Any, Dict, List, Optional, Protocol


class CategoriaFiscalGateway(Protocol):
    def list(self) -> List[Dict[str, Any]]: ...

    def get(self, categoria_fiscal_id: int) -> Optional[Dict[str, Any]]: ...
