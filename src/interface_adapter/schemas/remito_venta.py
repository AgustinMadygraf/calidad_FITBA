from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SimpleItem(BaseModel):
    ID: Optional[int] = None
    nombre: Optional[str] = None
    codigo: Optional[str] = None
    id: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class TransaccionProductoItem(BaseModel):
    transaccionCVItemId: Optional[int] = None
    precioconivaincluido: Optional[float] = None
    transaccionId: Optional[int] = None
    producto: Optional[SimpleItem] = None
    centroDeCosto: Optional[SimpleItem] = None
    deposito: Optional[SimpleItem] = None
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    precio: Optional[float] = None
    iva: Optional[float] = None
    importe: Optional[float] = None
    total: Optional[float] = None
    montoExento: Optional[float] = None
    porcentajeDescuento: Optional[float] = None

    model_config = ConfigDict(extra="allow")


class RemitoVentaPayload(BaseModel):
    transaccionId: Optional[int] = None
    clienteId: Optional[int] = None
    numeroRemito: Optional[str] = None
    fecha: Optional[str] = None
    vendedorId: Optional[int] = None
    comisionVendedor: Optional[float] = None
    sucursalClienteId: Optional[int] = None
    depositoId: Optional[int] = None
    transporteId: Optional[int] = None
    listaPrecioId: Optional[int] = None
    observacion: Optional[str] = None
    circuitoContableId: Optional[int] = None
    transaccionProductoItem: Optional[List[TransaccionProductoItem]] = None

    model_config = ConfigDict(extra="allow")
