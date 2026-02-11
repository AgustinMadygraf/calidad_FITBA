from ...entities.cliente import Cliente as ClienteEntity
from ...entities.cliente import Provincia as ProvinciaEntity
from ...entities.common import SimpleItem as SimpleItemEntity
from .schema_factory import model_from_entity

SimpleItem = model_from_entity("SimpleItem", SimpleItemEntity)
Provincia = model_from_entity("Provincia", ProvinciaEntity)

ClientePayload = model_from_entity(
    "ClientePayload",
    ClienteEntity,
    type_map={
        SimpleItemEntity: SimpleItem,
        ProvinciaEntity: Provincia,
    },
)
