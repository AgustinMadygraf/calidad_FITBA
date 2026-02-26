from typing import Any, Dict, Iterable

_REF_DEFAULT = {"ID": 0, "nombre": "", "codigo": "", "id": 0}
_PROVINCIA_DEFAULT = {
    "provincia_id": 0,
    "codigo": "",
    "nombre": "",
    "pais": None,
}
_ARRAY_FIELDS = (
    "transaccionProductoItems",
    "transaccionPercepcionItems",
    "transaccionCobranzaItems",
)
_REF_FIELDS = (
    "circuitoContable",
    "comprobante",
    "comprobanteAsociado",
    "cliente",
    "tipo",
    "condicionDePago",
    "deposito",
    "puntoVenta",
    "listaDePrecio",
    "vendedor",
)

_CONTRACT_FIELDS = (
    "circuitoContable",
    "comprobante",
    "comprobanteAsociado",
    "fechaDesde",
    "fechaHasta",
    "tienePeriodoServicio",
    "fechaFacturacionServicioDesde",
    "fechaFacturacionServicioHasta",
    "CAE",
    "transaccionid",
    "externalId",
    "cliente",
    "tipo",
    "nombre",
    "fecha",
    "fechaVto",
    "puntoVenta",
    "numeroDocumento",
    "condicionDePago",
    "deposito",
    "primerTktA",
    "ultimoTktA",
    "primerTktBC",
    "ultimoTktBC",
    "cantComprobantesEmitidos",
    "cantComprobantesCancelados",
    "cotizacion",
    "importeMonPrincipal",
    "importetotal",
    "importeImpuestos",
    "importeGravado",
    "origenId",
    "provincia",
    "cotizacionListaDePrecio",
    "listaDePrecio",
    "vendedor",
    "porcentajeComision",
    "mailEstado",
    "descripcion",
    "cbuinformada",
    "facturaNoExportacion",
    "transaccionProductoItems",
    "transaccionPercepcionItems",
    "transaccionCobranzaItems",
)

_DEFAULTS: Dict[str, Any] = {
    "fechaDesde": "",
    "fechaHasta": "",
    "tienePeriodoServicio": False,
    "fechaFacturacionServicioDesde": "",
    "fechaFacturacionServicioHasta": "",
    "CAE": "",
    "transaccionid": 0,
    "externalId": "",
    "nombre": "",
    "fecha": "",
    "fechaVto": "",
    "numeroDocumento": "",
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
    "cotizacionListaDePrecio": 0,
    "porcentajeComision": 0,
    "mailEstado": "",
    "descripcion": "",
    "cbuinformada": "",
    "facturaNoExportacion": False,
}


def _normalize_ref(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {
            "ID": value.get("ID", value.get("id", value.get("vendedorId", 0))),
            "nombre": value.get("nombre", ""),
            "codigo": value.get("codigo", ""),
            "id": value.get("id", value.get("ID", value.get("vendedorId", 0))),
        }
    return dict(_REF_DEFAULT)


def _normalize_provincia(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {
            "provincia_id": value.get(
                "provincia_id", value.get("ID", value.get("id", 0))
            ),
            "codigo": value.get("codigo", ""),
            "nombre": value.get("nombre", ""),
            "pais": value.get("pais"),
        }
    return dict(_PROVINCIA_DEFAULT)


def _get_cae(payload: Dict[str, Any]) -> Any:
    if "CAE" in payload:
        return payload.get("CAE")
    return payload.get("cae", "")


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
        if field == "CAE":
            value = _get_cae(payload)
            normalized[field] = "" if value is None else value
            continue

        value = payload.get(field)
        if value is None:
            value = _DEFAULTS.get(field, "")
        normalized[field] = value

    return normalized


def normalize_comprobante_venta_list(items: Iterable[Dict[str, Any]]) -> list[Dict[str, Any]]:
    return [normalize_comprobante_venta(item) for item in items]
