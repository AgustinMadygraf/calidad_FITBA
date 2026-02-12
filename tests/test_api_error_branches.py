from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from src.infrastructure.fastapi import api
from src.infrastructure.fastapi.api import app
from src.use_cases.errors import ExternalServiceError


def _raise_external(*_args, **_kwargs):
    raise ExternalServiceError("boom")


def _raise_value(*_args, **_kwargs):
    raise ValueError("bad input")


def test_lazy_gateway_getters_set_app_attributes(monkeypatch):
    cases = [
        ("cliente_gateway", "_get_cliente_gateway", "get_cliente_gateway"),
        ("categoria_fiscal_gateway", "_get_categoria_fiscal_gateway", "get_categoria_fiscal_gateway"),
        ("remito_gateway", "_get_remito_gateway", "get_remito_gateway"),
        ("producto_gateway", "_get_producto_gateway", "get_producto_gateway"),
        ("producto_compra_gateway", "_get_producto_compra_gateway", "get_producto_compra_gateway"),
        ("deposito_gateway", "_get_deposito_gateway", "get_deposito_gateway"),
        (
            "identificacion_tributaria_gateway",
            "_get_identificacion_tributaria_gateway",
            "get_identificacion_tributaria_gateway",
        ),
        ("lista_precio_gateway", "_get_lista_precio_gateway", "get_lista_precio_gateway"),
        ("moneda_gateway", "_get_moneda_gateway", "get_moneda_gateway"),
        ("vendedor_gateway", "_get_vendedor_gateway", "get_vendedor_gateway"),
        (
            "comprobante_venta_gateway",
            "_get_comprobante_venta_gateway",
            "get_comprobante_venta_gateway",
        ),
    ]
    for attr_name, getter_name, dep_factory_name in cases:
        sentinel = object()
        monkeypatch.setattr(api, dep_factory_name, lambda sentinel=sentinel: sentinel)
        monkeypatch.delattr(app, attr_name, raising=False)
        result = getattr(api, getter_name)()
        assert result is sentinel
        assert getattr(app, attr_name) is sentinel


def test_root_uses_frontend_file_when_available(tmp_path, monkeypatch):
    index = tmp_path / "index.html"
    index.write_text("<html>ok</html>", encoding="utf-8")
    monkeypatch.setattr(api, "FRONTEND_INDEX", index)
    response = api.root()
    assert Path(getattr(response, "path", "")) == index


def test_root_falls_back_to_handler_when_frontend_missing(monkeypatch):
    monkeypatch.setattr(api, "FRONTEND_INDEX", Path("/tmp/no-existe-fitba-index.html"))
    monkeypatch.setattr(api.handlers, "root", lambda: {"status": "ok", "message": "fallback"})
    assert api.root() == {"status": "ok", "message": "fallback"}


def test_favicon_and_health_cover_routes():
    assert api.favicon().status_code == 204
    assert api.health() == {"status": "ok"}


def test_token_inspect_returns_500_on_unexpected_error(monkeypatch):
    class ErrGateway:
        def get_status(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(api, "token_gateway", ErrGateway())
    with pytest.raises(Exception) as exc_info:
        api.token_inspect()
    assert getattr(exc_info.value, "status_code", None) == 500


def test_resolve_remito_transaccion_id_uses_path_when_body_missing():
    data = {}
    transaccion_id = api._resolve_remito_transaccion_id(data, path_transaccion_id=9)
    assert transaccion_id == 9
    assert data["transaccionId"] == 9


def test_resolve_remito_transaccion_id_rejects_invalid_type():
    with pytest.raises(Exception) as exc_info:
        api._resolve_remito_transaccion_id({"transaccionId": "abc"})
    assert getattr(exc_info.value, "status_code", None) == 400


def test_resolve_remito_transaccion_id_rejects_non_positive():
    with pytest.raises(Exception) as exc_info:
        api._resolve_remito_transaccion_id({"transaccionId": 0})
    assert getattr(exc_info.value, "status_code", None) == 400


def test_debug_route_returns_404_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    client = TestClient(app)
    response = client.get("/debug/clienteBean")
    assert response.status_code == 404


def test_debug_route_returns_502_on_gateway_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(api.handlers, "debug_clientes", _raise_external)
    client = TestClient(app)
    response = client.get("/debug/clienteBean")
    assert response.status_code == 502


@pytest.mark.parametrize(
    "path,handler_name",
    [
        ("/API/1.1/clienteBean", "list_clientes"),
        ("/API/1.1/categoriaFiscal", "list_categorias_fiscales"),
        ("/API/1.1/remitoVentaBean", "list_remitos"),
        ("/API/1.1/ProductoVentaBean", "list_productos"),
        ("/API/1.1/ProductoCompraBean", "list_productos"),
        ("/API/1.1/depositos", "list_depositos"),
        ("/API/1.1/identificacionTributaria", "list_identificaciones_tributarias"),
        ("/API/1.1/listaPrecioBean", "list_lista_precios"),
        ("/API/1.1/monedaBean", "list_monedas"),
        ("/API/1.1/vendedorBean", "list_vendedores"),
        ("/API/1.1/comprobanteVentaBean", "list_comprobantes_venta"),
    ],
)
def test_list_routes_return_502_on_external_errors(monkeypatch, path, handler_name):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(api.handlers, handler_name, _raise_external)
    client = TestClient(app)
    response = client.get(path)
    assert response.status_code == 502


@pytest.mark.parametrize(
    "path,handler_name",
    [
        ("/API/1.1/categoriaFiscal/1", "get_categoria_fiscal"),
        ("/API/1.1/clienteBean/1", "get_cliente"),
        ("/API/1.1/remitoVentaBean/1", "get_remito"),
        ("/API/1.1/ProductoVentaBean/1", "get_producto"),
        ("/API/1.1/ProductoCompraBean/1", "get_producto"),
        ("/API/1.1/depositos/1", "get_deposito"),
        ("/API/1.1/identificacionTributaria/1", "get_identificacion_tributaria"),
        ("/API/1.1/listaPrecioBean/1", "get_lista_precio"),
        ("/API/1.1/monedaBean/1", "get_moneda"),
        ("/API/1.1/vendedorBean/1", "get_vendedor"),
        ("/API/1.1/comprobanteVentaBean/1", "get_comprobante_venta"),
    ],
)
def test_get_routes_return_404_when_resource_not_found(monkeypatch, path, handler_name):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(api.handlers, handler_name, lambda *_args, **_kwargs: None)
    client = TestClient(app)
    response = client.get(path)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "path,handler_name",
    [
        ("/API/1.1/categoriaFiscal/1", "get_categoria_fiscal"),
        ("/API/1.1/clienteBean/1", "get_cliente"),
        ("/API/1.1/remitoVentaBean/1", "get_remito"),
        ("/API/1.1/ProductoVentaBean/1", "get_producto"),
        ("/API/1.1/ProductoCompraBean/1", "get_producto"),
        ("/API/1.1/depositos/1", "get_deposito"),
        ("/API/1.1/identificacionTributaria/1", "get_identificacion_tributaria"),
        ("/API/1.1/listaPrecioBean/1", "get_lista_precio"),
        ("/API/1.1/monedaBean/1", "get_moneda"),
        ("/API/1.1/vendedorBean/1", "get_vendedor"),
        ("/API/1.1/comprobanteVentaBean/1", "get_comprobante_venta"),
    ],
)
def test_get_routes_return_502_on_external_errors(monkeypatch, path, handler_name):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(api.handlers, handler_name, _raise_external)
    client = TestClient(app)
    response = client.get(path)
    assert response.status_code == 502


@pytest.mark.parametrize(
    "method,path,body,handler_name",
    [
        ("put", "/API/1.1/clienteBean/1", {}, "update_cliente"),
        ("delete", "/API/1.1/clienteBean/1", None, "delete_cliente"),
        ("put", "/API/1.1/remitoVentaBean", {"transaccionId": 1}, "update_remito"),
        ("put", "/API/1.1/remitoVentaBean/1", {}, "update_remito"),
        ("delete", "/API/1.1/remitoVentaBean/1", None, "delete_remito"),
        ("put", "/API/1.1/ProductoVentaBean/1", {}, "update_producto"),
        ("delete", "/API/1.1/ProductoVentaBean/1", None, "delete_producto"),
        ("put", "/API/1.1/listaPrecioBean/1", {}, "update_lista_precio"),
        ("patch", "/API/1.1/listaPrecioBean/1", {}, "patch_lista_precio"),
        ("delete", "/API/1.1/listaPrecioBean/1", None, "delete_lista_precio"),
    ],
)
def test_mutation_routes_return_404_when_resource_not_found(
    monkeypatch, method, path, body, handler_name
):
    monkeypatch.setenv("IS_PROD", "true")
    not_found_value = False if method == "delete" else None
    monkeypatch.setattr(
        api.handlers,
        handler_name,
        lambda *_args, **_kwargs: not_found_value,
    )
    client = TestClient(app)
    response = getattr(client, method)(path, json=body) if body is not None else getattr(client, method)(path)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "method,path,body,handler_name",
    [
        ("post", "/API/1.1/clienteBean", {}, "create_cliente"),
        ("put", "/API/1.1/clienteBean/1", {}, "update_cliente"),
        ("delete", "/API/1.1/clienteBean/1", None, "delete_cliente"),
        ("post", "/API/1.1/remitoVentaBean", {}, "create_remito"),
        ("put", "/API/1.1/remitoVentaBean", {"transaccionId": 1}, "update_remito"),
        ("put", "/API/1.1/remitoVentaBean/1", {}, "update_remito"),
        ("delete", "/API/1.1/remitoVentaBean/1", None, "delete_remito"),
        ("post", "/API/1.1/ProductoVentaBean", {}, "create_producto"),
        ("put", "/API/1.1/ProductoVentaBean/1", {}, "update_producto"),
        ("delete", "/API/1.1/ProductoVentaBean/1", None, "delete_producto"),
        ("post", "/API/1.1/listaPrecioBean", {}, "create_lista_precio"),
        ("put", "/API/1.1/listaPrecioBean/1", {}, "update_lista_precio"),
        ("patch", "/API/1.1/listaPrecioBean/1", {}, "patch_lista_precio"),
        ("delete", "/API/1.1/listaPrecioBean/1", None, "delete_lista_precio"),
    ],
)
def test_mutation_routes_return_502_on_external_errors(
    monkeypatch, method, path, body, handler_name
):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, handler_name, _raise_external)
    client = TestClient(app)
    response = getattr(client, method)(path, json=body) if body is not None else getattr(client, method)(path)
    assert response.status_code == 502


def test_cliente_create_returns_400_on_value_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, "create_cliente", _raise_value)
    client = TestClient(app)
    response = client.post("/API/1.1/clienteBean", json={})
    assert response.status_code == 400


def test_remito_create_returns_400_on_value_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, "create_remito", _raise_value)
    client = TestClient(app)
    response = client.post("/API/1.1/remitoVentaBean", json={})
    assert response.status_code == 400


def test_remito_put_by_body_returns_400_on_value_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, "update_remito", _raise_value)
    client = TestClient(app)
    response = client.put("/API/1.1/remitoVentaBean", json={"transaccionId": 1})
    assert response.status_code == 400


def test_remito_put_by_path_returns_400_on_value_error(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, "update_remito", _raise_value)
    client = TestClient(app)
    response = client.put("/API/1.1/remitoVentaBean/1", json={})
    assert response.status_code == 400


def test_remito_put_by_path_uses_path_transaccion_id_when_missing(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    captured = {}

    def fake_update(_gateway, _transaccion_id, _deps, data):
        captured["transaccionId"] = data.get("transaccionId")
        return {"transaccionId": data.get("transaccionId")}

    monkeypatch.setattr(api.handlers, "update_remito", fake_update)
    client = TestClient(app)
    response = client.put("/API/1.1/remitoVentaBean/9", json={})
    assert response.status_code == 200
    assert captured["transaccionId"] == 9


def test_run_invokes_uvicorn_with_resolved_host_and_port(monkeypatch):
    called = {}
    monkeypatch.setattr(api, "get_host", lambda: "127.0.0.9")
    monkeypatch.setattr(api, "get_port", lambda: 9001)
    monkeypatch.setattr(
        api,
        "uvicorn",
        SimpleNamespace(
            run=lambda *args, **kwargs: called.update({"args": args, "kwargs": kwargs})
        ),
    )
    api.run()
    assert called["args"] == ("src.infrastructure.fastapi.api:app",)
    assert called["kwargs"]["host"] == "127.0.0.9"
    assert called["kwargs"]["port"] == 9001
    assert called["kwargs"]["reload"] is True
