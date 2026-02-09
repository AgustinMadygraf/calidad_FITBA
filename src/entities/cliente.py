from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SimpleItem:
    ID: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    id: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["SimpleItem"]:
        if not data:
            return None
        return cls(
            ID=data.get("ID"),
            nombre=data.get("nombre"),
            codigo=data.get("codigo"),
            id=data.get("id"),
        )


@dataclass
class Provincia:
    provincia_id: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    pais: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Provincia"]:
        if not data:
            return None
        return cls(
            provincia_id=data.get("provincia_id"),
            codigo=data.get("codigo"),
            nombre=data.get("nombre"),
            pais=data.get("pais"),
        )


@dataclass
class Cliente:
    cliente_id: Optional[int] = None
    nombre: Optional[str] = None
    primerApellido: Optional[str] = None
    segundoApellido: Optional[str] = None
    primerNombre: Optional[str] = None
    otrosNombres: Optional[str] = None
    razonSocial: Optional[str] = None
    nombreComercial: Optional[str] = None
    identificacionTributaria: Optional[SimpleItem] = None
    digitoVerificacion: Optional[str] = None
    categoriaFiscal: Optional[SimpleItem] = None
    provincia: Optional[Provincia] = None
    direccion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    codigoPostal: Optional[str] = None
    cuentaVenta_id: Optional[SimpleItem] = None
    cuentaCompra_id: Optional[SimpleItem] = None
    pais: Optional[SimpleItem] = None
    localidad: Optional[SimpleItem] = None
    usrCode: Optional[str] = None
    listaPrecioVenta: Optional[SimpleItem] = None
    descripcion: Optional[str] = None
    esclienteextranjero: Optional[int] = None
    esProveedor: Optional[int] = None
    cuit: Optional[str] = None
    tipoDeOrganizacion: Optional[SimpleItem] = None
    responsabilidadOrganizacionItem: List[SimpleItem] = field(default_factory=list)
    CUIT: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cliente":
        items = data.get("responsabilidadOrganizacionItem") or []
        return cls(
            cliente_id=data.get("cliente_id"),
            nombre=data.get("nombre"),
            primerApellido=data.get("primerApellido"),
            segundoApellido=data.get("segundoApellido"),
            primerNombre=data.get("primerNombre"),
            otrosNombres=data.get("otrosNombres"),
            razonSocial=data.get("razonSocial"),
            nombreComercial=data.get("nombreComercial"),
            identificacionTributaria=SimpleItem.from_dict(data.get("identificacionTributaria")),
            digitoVerificacion=data.get("digitoVerificacion"),
            categoriaFiscal=SimpleItem.from_dict(data.get("categoriaFiscal")),
            provincia=Provincia.from_dict(data.get("provincia")),
            direccion=data.get("direccion"),
            email=data.get("email"),
            telefono=data.get("telefono"),
            codigoPostal=data.get("codigoPostal"),
            cuentaVenta_id=SimpleItem.from_dict(data.get("cuentaVenta_id")),
            cuentaCompra_id=SimpleItem.from_dict(data.get("cuentaCompra_id")),
            pais=SimpleItem.from_dict(data.get("pais")),
            localidad=SimpleItem.from_dict(data.get("localidad")),
            usrCode=data.get("usrCode"),
            listaPrecioVenta=SimpleItem.from_dict(data.get("listaPrecioVenta")),
            descripcion=data.get("descripcion"),
            esclienteextranjero=data.get("esclienteextranjero"),
            esProveedor=data.get("esProveedor"),
            cuit=data.get("cuit"),
            tipoDeOrganizacion=SimpleItem.from_dict(data.get("tipoDeOrganizacion")),
            responsabilidadOrganizacionItem=[
                item for item in (SimpleItem.from_dict(x) for x in items) if item is not None
            ],
            CUIT=data.get("CUIT"),
        )

    def to_dict(self, *, exclude_none: bool = False) -> Dict[str, Any]:
        data = asdict(self)
        if exclude_none:
            return _drop_none(data)
        return data


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_none(v) for v in value]
    return value
