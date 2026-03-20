from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from .common import SimpleItem, drop_none


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
class ClienteIdentidad:
    nombre: Optional[str] = None
    primerApellido: Optional[str] = None
    segundoApellido: Optional[str] = None
    primerNombre: Optional[str] = None
    otrosNombres: Optional[str] = None
    razonSocial: Optional[str] = None
    nombreComercial: Optional[str] = None


@dataclass
class ClienteFiscal:
    identificacionTributaria: Optional[SimpleItem] = None
    digitoVerificacion: Optional[str] = None
    categoriaFiscal: Optional[SimpleItem] = None
    cuit: Optional[str] = None
    CUIT: Optional[str] = None
    tipoDeOrganizacion: Optional[SimpleItem] = None
    responsabilidadOrganizacionItem: List[SimpleItem] = field(default_factory=list)
    esclienteextranjero: Optional[int] = None
    esProveedor: Optional[int] = None


@dataclass
class ClienteContacto:
    direccion: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    codigoPostal: Optional[str] = None


@dataclass
class ClienteUbicacion:
    provincia: Optional[Provincia] = None
    pais: Optional[SimpleItem] = None
    localidad: Optional[SimpleItem] = None


@dataclass
class ClienteCuentas:
    cuentaVenta_id: Optional[SimpleItem] = None
    cuentaCompra_id: Optional[SimpleItem] = None
    listaPrecioVenta: Optional[SimpleItem] = None


@dataclass
class ClienteExtra:
    usrCode: Optional[str] = None
    descripcion: Optional[str] = None


@dataclass
class Cliente:
    cliente_id: Optional[int] = None
    identidad: ClienteIdentidad = field(
        default_factory=ClienteIdentidad, metadata={"flatten": True}
    )
    fiscal: ClienteFiscal = field(
        default_factory=ClienteFiscal, metadata={"flatten": True}
    )
    contacto: ClienteContacto = field(
        default_factory=ClienteContacto, metadata={"flatten": True}
    )
    ubicacion: ClienteUbicacion = field(
        default_factory=ClienteUbicacion, metadata={"flatten": True}
    )
    cuentas: ClienteCuentas = field(
        default_factory=ClienteCuentas, metadata={"flatten": True}
    )
    extra: ClienteExtra = field(
        default_factory=ClienteExtra, metadata={"flatten": True}
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Cliente":
        items = data.get("responsabilidadOrganizacionItem") or []
        return cls(
            cliente_id=data.get("cliente_id"),
            identidad=ClienteIdentidad(
                nombre=data.get("nombre"),
                primerApellido=data.get("primerApellido"),
                segundoApellido=data.get("segundoApellido"),
                primerNombre=data.get("primerNombre"),
                otrosNombres=data.get("otrosNombres"),
                razonSocial=data.get("razonSocial"),
                nombreComercial=data.get("nombreComercial"),
            ),
            fiscal=ClienteFiscal(
                identificacionTributaria=SimpleItem.from_dict(
                    data.get("identificacionTributaria")
                ),
                digitoVerificacion=data.get("digitoVerificacion"),
                categoriaFiscal=SimpleItem.from_dict(data.get("categoriaFiscal")),
                cuit=data.get("cuit"),
                CUIT=data.get("CUIT"),
                tipoDeOrganizacion=SimpleItem.from_dict(data.get("tipoDeOrganizacion")),
                responsabilidadOrganizacionItem=[
                    item
                    for item in (SimpleItem.from_dict(x) for x in items)
                    if item is not None
                ],
                esclienteextranjero=data.get("esclienteextranjero"),
                esProveedor=data.get("esProveedor"),
            ),
            contacto=ClienteContacto(
                direccion=data.get("direccion"),
                email=data.get("email"),
                telefono=data.get("telefono"),
                codigoPostal=data.get("codigoPostal"),
            ),
            ubicacion=ClienteUbicacion(
                provincia=Provincia.from_dict(data.get("provincia")),
                pais=SimpleItem.from_dict(data.get("pais")),
                localidad=SimpleItem.from_dict(data.get("localidad")),
            ),
            cuentas=ClienteCuentas(
                cuentaVenta_id=SimpleItem.from_dict(data.get("cuentaVenta_id")),
                cuentaCompra_id=SimpleItem.from_dict(data.get("cuentaCompra_id")),
                listaPrecioVenta=SimpleItem.from_dict(data.get("listaPrecioVenta")),
            ),
            extra=ClienteExtra(
                usrCode=data.get("usrCode"),
                descripcion=data.get("descripcion"),
            ),
        )

    def to_dict(self, *, exclude_none: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "cliente_id": self.cliente_id,
            **asdict(self.identidad),
            **asdict(self.fiscal),
            **asdict(self.contacto),
            **asdict(self.ubicacion),
            **asdict(self.cuentas),
            **asdict(self.extra),
        }
        if exclude_none:
            return drop_none(data)
        return data
