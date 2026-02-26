from typing import Any, Dict, Iterable

_REF_DEFAULT = {"ID": 0, "nombre": "", "codigo": "", "id": 0}
_PROVINCIA_DEFAULT = {"ID": 0, "nombre": "", "codigo": "", "id": 0}
_ARRAY_FIELDS = (
    "transaccionProductoItems",
    "transaccionPercepcionItems",
    "transaccionCobranzaItems",
    "caefechaVto",
)
_REF_FIELDS = (
    "moneda",
    "circuitoContable",
    "deposito",
    "puntoVenta",
    "cliente",
)

_CONTRACT_FIELDS = (
    "numeroDocumento",
    "descripcion",
    "fecha",
    "importeGravado",
    "importeImpuestos",
    "importetotal",
    "moneda",
    "circuitoContable",
    "cotizacion",
    "fechaVto",
    "cotizacionListaDePrecio",
    "deposito",
    "provincia",
    "condicionDePago",
    "transaccionid",
    "porcentajeComision",
    "transaccionProductoItems",
    "puntoVenta",
    "facturaNoExportacion",
    "cliente",
    "tipo",
    "transaccionPercepcionItems",
    "transaccionCobranzaItems",
    "cbuinformada",
    "cae",
    "caefechaVto",
    "CAE",
)

_DEFAULTS: Dict[str, Any] = {
    "numeroDocumento": "",
    "descripcion": "",
    "fecha": "",
    "importeGravado": 0,
    "importeImpuestos": 0,
    "importetotal": 0,
    "cotizacion": 0,
    "fechaVto": "",
    "cotizacionListaDePrecio": 0,
    "condicionDePago": 0,
    "transaccionid": 0,
    "porcentajeComision": 0,
    "facturaNoExportacion": False,
    "tipo": 0,
    "cbuinformada": False,
    "cae": "",
    "CAE": "",
}


def _normalize_ref(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {
            "ID": value.get("ID", value.get("id", 0)),
            "nombre": value.get("nombre", ""),
            "codigo": value.get("codigo", ""),
            "id": value.get("id", value.get("ID", 0)),
        }
    return dict(_REF_DEFAULT)


def _normalize_provincia(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        pid = value.get("ID", value.get("id", value.get("provincia_id", 0)))
        return {
            "ID": pid,
            "nombre": value.get("nombre", ""),
            "codigo": value.get("codigo", ""),
            "id": value.get("id", pid),
        }
    return dict(_PROVINCIA_DEFAULT)


def _get_cae(payload: Dict[str, Any]) -> Any:
    if "cae" in payload and payload.get("cae") is not None:
        return payload.get("cae")
    if "CAE" in payload and payload.get("CAE") is not None:
        return payload.get("CAE")
    return ""


def normalize_comprobante_venta(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized: Dict[str, Any] = {}

    for field in _CONTRACT_FIELDS:
        if field in _REF_FIELDS:
            normalized[field] = _normalize_ref(payload.get(field))
            continue
        if field == "provincia":
            normalized[field] = _normalize_provincia(payload.get(field))
            continue
        if field in _ARRAY_FIELDS:
            value = payload.get(field)
            normalized[field] = value if isinstance(value, list) else []
            continue
        if field in ("cae", "CAE"):
            normalized[field] = _get_cae(payload)
            continue

        value = payload.get(field)
        if value is None:
            value = _DEFAULTS.get(field, "")
        normalized[field] = value

    return normalized


def normalize_comprobante_venta_list(items: Iterable[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [normalize_comprobante_venta(item) for item in items]
