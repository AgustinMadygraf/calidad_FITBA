def test_memory_gateway_crud(cliente_gateway):
    gw = cliente_gateway
    created = gw.create({"nombre": "A", "cliente_id": 99})
    assert created["cliente_id"] == 1

    listed = gw.list()
    assert len(listed) == 1

    got = gw.get(1)
    assert got is not None
    assert got["nombre"] == "A"

    updated = gw.update(1, {"nombre": "B"})
    assert updated is not None
    assert updated["nombre"] == "B"

    missing_update = gw.update(999, {"nombre": "X"})
    assert missing_update is None

    assert gw.delete(1) is True
    assert gw.delete(1) is False
