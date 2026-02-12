from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway


def test_producto_memory_gateway_crud():
    gw = InMemoryProductoGateway()

    created = gw.create({"nombre": "P1"})
    assert created["productoid"] == 1
    assert gw.list() == [{"nombre": "P1", "productoid": 1}]
    assert gw.get(1) == {"nombre": "P1", "productoid": 1}

    updated = gw.update(1, {"nombre": "P1-upd"})
    assert updated == {"nombre": "P1-upd", "productoid": 1}
    assert gw.update(99, {"nombre": "missing"}) is None

    assert gw.delete(1) is True
    assert gw.delete(1) is False

