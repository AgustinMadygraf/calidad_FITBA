from src.infrastructure.memory.remito_gateway_memory import InMemoryRemitoGateway


def test_remito_memory_gateway_crud():
    gw = InMemoryRemitoGateway()
    created = gw.create({"numeroRemito": "R-1"})
    assert created["transaccionId"] == 1

    listed = gw.list()
    assert len(listed) == 1

    got = gw.get(1)
    assert got is not None
    assert got["numeroRemito"] == "R-1"

    updated = gw.update(1, {"observacion": "ok"})
    assert updated is not None
    assert updated["observacion"] == "ok"

    missing_update = gw.update(999, {"observacion": "x"})
    assert missing_update is None

    assert gw.delete(1) is True
    assert gw.delete(1) is False
