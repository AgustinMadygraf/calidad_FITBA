from ...entities.common import SimpleItem as SimpleItemEntity
from ...entities.remito_venta import RemitoVenta as RemitoVentaEntity
from ...entities.remito_venta import TransaccionProductoItem as ItemEntity
from .schema_factory import model_from_entity

SimpleItem = model_from_entity("SimpleItem", SimpleItemEntity)
TransaccionProductoItem = model_from_entity(
    "TransaccionProductoItem",
    ItemEntity,
    type_map={SimpleItemEntity: SimpleItem},
)

RemitoVentaPayload = model_from_entity(
    "RemitoVentaPayload",
    RemitoVentaEntity,
    type_map={SimpleItemEntity: SimpleItem, ItemEntity: TransaccionProductoItem},
)
