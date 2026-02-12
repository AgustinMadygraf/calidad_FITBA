from src.entities.cliente import Cliente
from src.interface_adapter.mappers import cliente_mapper


def test_to_entity_maps_payload():
    entity = cliente_mapper.to_entity({"nombre": "ACME"})

    assert isinstance(entity, Cliente)
    assert entity.identidad.nombre == "ACME"


def test_to_dict_respects_exclude_none():
    entity = Cliente.from_dict({"nombre": "ACME"})

    full = cliente_mapper.to_dict(entity, exclude_none=False)
    compact = cliente_mapper.to_dict(entity, exclude_none=True)

    assert "nombre" in full
    assert "nombre" in compact
    assert "email" in full
    assert "email" not in compact

