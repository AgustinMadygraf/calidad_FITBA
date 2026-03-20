from src.entities.cliente import Cliente
from src.entities.remito_venta import RemitoVenta
from src.interface_adapter.controllers import handlers


class _CrudGateway:
    def __init__(self):
        self._items = [{"id": 1}]

    def list(self):
        return self._items

    def get(self, _item_id):
        return {"id": 1}

    def create(self, data):
        return data

    def update(self, _item_id, data):
        return data

    def patch(self, _item_id, data):
        return data

    def delete(self, _item_id):
        return True


def test_root_and_health():
    assert handlers.root()["status"] == "ok"
    assert handlers.health() == {"status": "ok"}


def test_inspect_token_calls_use_case_and_presenter(monkeypatch):
    monkeypatch.setattr(
        handlers.token_inspect, "execute", lambda _gateway: {"token_preview": "abc"}
    )
    monkeypatch.setattr(
        handlers.token_presenter, "present", lambda status: {"presented": status}
    )

    payload = handlers.inspect_token(object())

    assert payload == {"presented": {"token_preview": "abc"}}


def test_cliente_wrappers(monkeypatch):
    clientes = [Cliente.from_dict({"nombre": "A"}), Cliente.from_dict({"nombre": "B"})]
    monkeypatch.setattr(handlers.cliente, "list_clientes", lambda _gateway: clientes)
    monkeypatch.setattr(handlers.cliente, "get_cliente", lambda _gateway, _cid: clientes[0])
    monkeypatch.setattr(
        handlers.cliente, "create_cliente", lambda _gw, entity, _deps: entity
    )
    monkeypatch.setattr(
        handlers.cliente, "update_cliente", lambda _gw, _cid, entity, _deps: entity
    )
    monkeypatch.setattr(handlers.cliente, "delete_cliente", lambda _gw, _cid: True)

    listed = handlers.list_clientes(object())
    debugged = handlers.debug_clientes(object())
    got = handlers.get_cliente(object(), 1)
    created = handlers.create_cliente(object(), object(), {"nombre": "C"})
    updated = handlers.update_cliente(object(), 1, object(), {"nombre": "D"})
    deleted = handlers.delete_cliente(object(), 1)

    assert len(listed["items"]) == 2
    assert debugged["count"] == 2
    assert len(debugged["sample"]) == 2
    assert got is not None and got["nombre"] == "A"
    assert created["nombre"] == "C"
    assert updated is not None and updated["nombre"] == "D"
    assert deleted is True


def test_cliente_get_and_update_return_none(monkeypatch):
    monkeypatch.setattr(handlers.cliente, "get_cliente", lambda _gateway, _cid: None)
    monkeypatch.setattr(
        handlers.cliente, "update_cliente", lambda _gw, _cid, _entity, _deps: None
    )

    assert handlers.get_cliente(object(), 1) is None
    assert handlers.update_cliente(object(), 1, object(), {"nombre": "X"}) is None


def test_remito_wrappers(monkeypatch):
    remito = RemitoVenta.from_dict({"transaccionId": 1, "clienteId": 1, "fecha": "2026-02-10"})
    monkeypatch.setattr(handlers.remito_venta, "list_remitos", lambda _gateway: [remito])
    monkeypatch.setattr(handlers.remito_venta, "get_remito", lambda _gateway, _tid: remito)
    monkeypatch.setattr(
        handlers.remito_venta, "create_remito", lambda _gw, entity, _deps: entity
    )
    monkeypatch.setattr(
        handlers.remito_venta, "update_remito", lambda _gw, _tid, entity, _deps: entity
    )
    monkeypatch.setattr(handlers.remito_venta, "delete_remito", lambda _gw, _tid: True)

    listed = handlers.list_remitos(object())
    got = handlers.get_remito(object(), 1)
    created = handlers.create_remito(
        object(), object(), {"clienteId": 1, "fecha": "2026-02-10"}
    )
    updated = handlers.update_remito(
        object(), 1, object(), {"clienteId": 1, "fecha": "2026-02-10"}
    )
    deleted = handlers.delete_remito(object(), 1)

    assert listed["items"][0]["transaccionId"] == 1
    assert got is not None and got["transaccionId"] == 1
    assert created["clienteId"] == 1
    assert updated is not None and updated["clienteId"] == 1
    assert deleted is True


def test_remito_get_and_update_return_none(monkeypatch):
    monkeypatch.setattr(handlers.remito_venta, "get_remito", lambda _gateway, _tid: None)
    monkeypatch.setattr(
        handlers.remito_venta, "update_remito", lambda _gw, _tid, _entity, _deps: None
    )

    assert handlers.get_remito(object(), 1) is None
    assert handlers.update_remito(object(), 1, object(), {"clienteId": 1}) is None


def test_generic_gateway_wrappers():
    gateway = _CrudGateway()

    assert handlers.list_productos(gateway) == {"items": [{"id": 1}]}
    assert handlers.list_categorias_fiscales(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_categoria_fiscal(gateway, 1) == {"id": 1}
    assert handlers.get_producto(gateway, 1) == {"id": 1}
    assert handlers.create_producto(gateway, {"nombre": "P"}) == {"nombre": "P"}
    assert handlers.update_producto(gateway, 1, {"nombre": "U"}) == {"nombre": "U"}
    assert handlers.delete_producto(gateway, 1) is True
    assert handlers.list_depositos(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_deposito(gateway, 1) == {"id": 1}
    assert handlers.list_identificaciones_tributarias(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_identificacion_tributaria(gateway, 1) == {"id": 1}
    assert handlers.list_lista_precios(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_lista_precio(gateway, 1) == {"id": 1}
    assert handlers.create_lista_precio(gateway, {"nombre": "LP"}) == {"nombre": "LP"}
    assert handlers.update_lista_precio(gateway, 1, {"nombre": "LP2"}) == {
        "nombre": "LP2"
    }
    assert handlers.patch_lista_precio(gateway, 1, {"descripcion": "x"}) == {
        "descripcion": "x"
    }
    assert handlers.delete_lista_precio(gateway, 1) is True
    assert handlers.list_monedas(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_moneda(gateway, 1) == {"id": 1}
    assert handlers.list_comprobantes_venta(gateway) == {"items": [{"id": 1}]}
    assert handlers.get_comprobante_venta(gateway, 1) == {"id": 1}
