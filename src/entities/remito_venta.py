from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
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
class TransaccionProductoItem:
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

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["TransaccionProductoItem"]:
        if not data:
            return None
        return cls(
            transaccionCVItemId=data.get("transaccionCVItemId"),
            precioconivaincluido=data.get("precioconivaincluido"),
            transaccionId=data.get("transaccionId"),
            producto=SimpleItem.from_dict(data.get("producto")),
            centroDeCosto=SimpleItem.from_dict(data.get("centroDeCosto")),
            deposito=SimpleItem.from_dict(data.get("deposito")),
            descripcion=data.get("descripcion"),
            cantidad=data.get("cantidad"),
            precio=data.get("precio"),
            iva=data.get("iva"),
            importe=data.get("importe"),
            total=data.get("total"),
            montoExento=data.get("montoExento"),
            porcentajeDescuento=data.get("porcentajeDescuento"),
        )


@dataclass
class RemitoVenta:
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
    transaccionProductoItem: List[TransaccionProductoItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemitoVenta":
        _validate_fecha(data.get("fecha"))
        _validate_positive(data.get("clienteId"), "clienteId")
        items = data.get("transaccionProductoItem") or []
        return cls(
            transaccionId=data.get("transaccionId"),
            clienteId=data.get("clienteId"),
            numeroRemito=data.get("numeroRemito"),
            fecha=data.get("fecha"),
            vendedorId=data.get("vendedorId"),
            comisionVendedor=data.get("comisionVendedor"),
            sucursalClienteId=data.get("sucursalClienteId"),
            depositoId=data.get("depositoId"),
            transporteId=data.get("transporteId"),
            listaPrecioId=data.get("listaPrecioId"),
            observacion=data.get("observacion"),
            circuitoContableId=data.get("circuitoContableId"),
            transaccionProductoItem=[
                item
                for item in (TransaccionProductoItem.from_dict(x) for x in items)
                if item is not None
            ],
        )

    def to_dict(self, *, exclude_none: bool = False) -> Dict[str, Any]:
        data = asdict(self)
        if exclude_none:
            return _drop_none(data)
        return data

    def validate(self) -> None:
        _validate_fecha(self.fecha)
        _validate_positive(self.clienteId, "clienteId")
        for item in self.transaccionProductoItem:
            _validate_positive(item.cantidad, "cantidad")
            _validate_positive(item.precio, "precio")
            _validate_non_negative(item.iva, "iva")
            _validate_non_negative(item.importe, "importe")
            _validate_non_negative(item.total, "total")
            _validate_non_negative(item.montoExento, "montoExento")
            _validate_non_negative(item.porcentajeDescuento, "porcentajeDescuento")


def _drop_none(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_none(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_drop_none(v) for v in value]
    return value


def _validate_fecha(value: Optional[str]) -> None:
    if value is None:
        return
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("fecha debe ser ISO YYYY-MM-DD") from exc


def _validate_positive(value: Optional[float], field_name: str) -> None:
    if value is None:
        return
    if value <= 0:
        raise ValueError(f"{field_name} debe ser > 0")


def _validate_non_negative(value: Optional[float], field_name: str) -> None:
    if value is None:
        return
    if value < 0:
        raise ValueError(f"{field_name} debe ser >= 0")
