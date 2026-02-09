from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SimpleItem(BaseModel):
    ID: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    id: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class Provincia(BaseModel):
    provincia_id: Optional[int] = None
    codigo: Optional[str] = None
    nombre: Optional[str] = None
    pais: Optional[str] = None

    model_config = ConfigDict(extra="allow")


class ClientePayload(BaseModel):
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
    responsabilidadOrganizacionItem: Optional[List[SimpleItem]] = None
    CUIT: Optional[str] = None

    model_config = ConfigDict(extra="allow")
