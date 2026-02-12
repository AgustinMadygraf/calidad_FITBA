"""
Path: src/infrastructure/memory/comprobante_venta_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...use_cases.ports.comprobante_venta_gateway import ComprobanteVentaGateway


_DEFAULT_COMPROBANTES_VENTA: List[Dict[str, Any]] = [
    {
        "transaccionid": 0,
        "externalId": "string",
        "nombre": "string",
        "fecha": "2018-12-31",
        "importetotal": 0,
        "cliente": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "vendedor": {
            "vendedorId": 0,
            "nombre": "string",
            "apellido": "string",
            "esVendedor": 0,
            "activo": 0,
        },
        "id": 0,
    }
]


class InMemoryComprobanteVentaGateway(ComprobanteVentaGateway):
    def __init__(self, items: Optional[List[Dict[str, Any]]] = None) -> None:
        source = items if items is not None else _DEFAULT_COMPROBANTES_VENTA
        self._items = [dict(item) for item in source]

    def list(self) -> List[Dict[str, Any]]:
        return [dict(item) for item in self._items]

    def get(self, comprobante_id: int) -> Optional[Dict[str, Any]]:
        for item in self._items:
            if item.get("transaccionid") == comprobante_id:
                return dict(item)
            if item.get("transaccionId") == comprobante_id:
                return dict(item)
            if item.get("ID") == comprobante_id:
                return dict(item)
            if item.get("id") == comprobante_id:
                return dict(item)
        return None
