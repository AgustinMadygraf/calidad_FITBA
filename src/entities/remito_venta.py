from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from .common import SimpleItem, drop_none


@dataclass
class ItemRefs:
    transaccionCVItemId: Optional[int] = None
    transaccionId: Optional[int] = None
    centroDeCosto: Optional[SimpleItem] = None
    deposito: Optional[SimpleItem] = None


@dataclass
class ItemProducto:
    productoId: Optional[int] = None
    productoid: Optional[int] = None
    producto: Optional[SimpleItem] = None


@dataclass
class ItemValores:
    precioconivaincluido: Optional[float] = None
    descripcion: Optional[str] = None
    cantidad: Optional[float] = None
    precio: Optional[float] = None
    iva: Optional[float] = None
    importe: Optional[float] = None
    total: Optional[float] = None
    montoExento: Optional[float] = None
    porcentajeDescuento: Optional[float] = None


@dataclass
class TransaccionProductoItem:
    refs: ItemRefs = field(default_factory=ItemRefs, metadata={"flatten": True})
    producto_ref: ItemProducto = field(
        default_factory=ItemProducto, metadata={"flatten": True}
    )
    valores: ItemValores = field(
        default_factory=ItemValores, metadata={"flatten": True}
    )

    @classmethod
    def from_dict(
        cls, data: Optional[Dict[str, Any]]
    ) -> Optional["TransaccionProductoItem"]:
        if not data:
            return None
        return cls(
            refs=ItemRefs(
                transaccionCVItemId=data.get("transaccionCVItemId"),
                transaccionId=data.get("transaccionId"),
                centroDeCosto=SimpleItem.from_dict(data.get("centroDeCosto")),
                deposito=SimpleItem.from_dict(data.get("deposito")),
            ),
            producto_ref=ItemProducto(
                productoId=data.get("productoId"),
                productoid=data.get("productoid"),
                producto=SimpleItem.from_dict(data.get("producto")),
            ),
            valores=ItemValores(
                precioconivaincluido=data.get("precioconivaincluido"),
                descripcion=data.get("descripcion"),
                cantidad=data.get("cantidad"),
                precio=data.get("precio"),
                iva=data.get("iva"),
                importe=data.get("importe"),
                total=data.get("total"),
                montoExento=data.get("montoExento"),
                porcentajeDescuento=data.get("porcentajeDescuento"),
            ),
        )


@dataclass
class RemitoEncabezado:
    numeroRemito: Optional[str] = None
    fecha: Optional[str] = None
    observacion: Optional[str] = None


@dataclass
class RemitoRelaciones:
    clienteId: Optional[int] = None
    vendedorId: Optional[int] = None
    comisionVendedor: Optional[float] = None
    sucursalClienteId: Optional[int] = None
    depositoId: Optional[int] = None
    transporteId: Optional[int] = None
    listaPrecioId: Optional[int] = None
    circuitoContableId: Optional[int] = None


@dataclass
class RemitoVenta:
    transaccionId: Optional[int] = None
    encabezado: RemitoEncabezado = field(
        default_factory=RemitoEncabezado, metadata={"flatten": True}
    )
    relaciones: RemitoRelaciones = field(
        default_factory=RemitoRelaciones, metadata={"flatten": True}
    )
    transaccionProductoItem: List[TransaccionProductoItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RemitoVenta":
        _validate_fecha(data.get("fecha"))
        _validate_positive(data.get("clienteId"), "clienteId")
        items = data.get("transaccionProductoItem") or []
        return cls(
            transaccionId=data.get("transaccionId"),
            encabezado=RemitoEncabezado(
                numeroRemito=data.get("numeroRemito"),
                fecha=data.get("fecha"),
                observacion=data.get("observacion"),
            ),
            relaciones=RemitoRelaciones(
                clienteId=data.get("clienteId"),
                vendedorId=data.get("vendedorId"),
                comisionVendedor=data.get("comisionVendedor"),
                sucursalClienteId=data.get("sucursalClienteId"),
                depositoId=data.get("depositoId"),
                transporteId=data.get("transporteId"),
                listaPrecioId=data.get("listaPrecioId"),
                circuitoContableId=data.get("circuitoContableId"),
            ),
            transaccionProductoItem=[
                item
                for item in (TransaccionProductoItem.from_dict(x) for x in items)
                if item is not None
            ],
        )

    def to_dict(self, *, exclude_none: bool = False) -> Dict[str, Any]:
        data = {
            "transaccionId": self.transaccionId,
            **asdict(self.encabezado),
            **asdict(self.relaciones),
            "transaccionProductoItem": [
                _item_to_dict(item) for item in self.transaccionProductoItem
            ],
        }
        if exclude_none:
            return drop_none(data)
        return data

    def validate(self) -> None:
        _validate_fecha(self.encabezado.fecha)
        _validate_positive(self.relaciones.clienteId, "clienteId")
        for item in self.transaccionProductoItem:
            _validate_positive(item.valores.cantidad, "cantidad")
            _validate_positive(item.valores.precio, "precio")
            _validate_non_negative(item.valores.iva, "iva")
            _validate_non_negative(item.valores.importe, "importe")
            _validate_non_negative(item.valores.total, "total")
            _validate_non_negative(item.valores.montoExento, "montoExento")
            _validate_non_negative(
                item.valores.porcentajeDescuento, "porcentajeDescuento"
            )


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


def _item_to_dict(item: TransaccionProductoItem) -> Dict[str, Any]:
    return {
        **asdict(item.refs),
        **asdict(item.producto_ref),
        **asdict(item.valores),
    }
