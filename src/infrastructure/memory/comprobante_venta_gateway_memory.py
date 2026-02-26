"""
Path: src/infrastructure/memory/comprobante_venta_gateway_memory.py
"""

from typing import Any, Dict, List, Optional

from ...shared.id_mapping import match_any_id
from ...use_cases.ports.comprobante_venta_gateway import ComprobanteVentaGateway


_DEFAULT_COMPROBANTES_VENTA: List[Dict[str, Any]] = [
    {
        "circuitoContable": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "comprobante": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "comprobanteAsociado": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "fechaDesde": "",
        "fechaHasta": "",
        "tienePeriodoServicio": False,
        "fechaFacturacionServicioDesde": "",
        "fechaFacturacionServicioHasta": "",
        "CAE": "",
        "transaccionid": 0,
        "externalId": "string",
        "nombre": "string",
        "fecha": "2018-12-31",
        "fechaVto": "",
        "puntoVenta": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "numeroDocumento": "string",
        "condicionDePago": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "deposito": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "primerTktA": 0,
        "ultimoTktA": 0,
        "primerTktBC": 0,
        "ultimoTktBC": 0,
        "cantComprobantesEmitidos": 0,
        "cantComprobantesCancelados": 0,
        "cotizacion": 0,
        "importeMonPrincipal": 0,
        "importetotal": 0,
        "importeImpuestos": 0,
        "importeGravado": 0,
        "origenId": 0,
        "provincia": {"provincia_id": 0, "codigo": "string", "nombre": "string", "pais": None},
        "cotizacionListaDePrecio": 0,
        "listaDePrecio": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "cliente": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "tipo": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "vendedor": {"ID": 0, "nombre": "string", "codigo": "string", "id": 0},
        "porcentajeComision": 0,
        "mailEstado": "",
        "descripcion": "",
        "cbuinformada": "",
        "facturaNoExportacion": False,
        "transaccionProductoItems": [],
        "transaccionPercepcionItems": [],
        "transaccionCobranzaItems": [],
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
            if match_any_id(
                item, comprobante_id, ("transaccionid", "transaccionId", "ID", "id")
            ):
                return dict(item)
        return None
