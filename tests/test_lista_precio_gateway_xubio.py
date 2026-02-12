import httpx
import pytest

import src.infrastructure.httpx.lista_precio_gateway_xubio as lista_precio_gateway
from src.infrastructure.httpx.lista_precio_gateway_xubio import XubioListaPrecioGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    lista_precio_gateway._GLOBAL_LIST_CACHE.clear()
    yield
    lista_precio_gateway._GLOBAL_LIST_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway()
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200, json={"items": [{"codigo": "LP2", "id": 2, "ID": 2}]}
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway()
    assert gw.list() == [{"codigo": "LP2", "id": 2, "ID": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_reads_from_list_only(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/listaPrecioBean/2"):
            raise AssertionError("No debe llamar al endpoint detalle de listaPrecio")
        if url.endswith("/listaPrecioBean"):
            return httpx.Response(200, json=[{"codigo": "LP2", "id": 2, "ID": 2}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway()
    assert gw.get(2) == {"codigo": "LP2", "id": 2, "ID": 2}


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["count"] == 1


def test_create_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "create": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])
        if method == "POST" and url.endswith("/listaPrecioBean"):
            calls["create"] += 1
            return httpx.Response(200, json={"codigo": "LP2", "id": 2, "ID": 2})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 1

    assert gw.create({"nombre": "LP2"}) == {"codigo": "LP2", "id": 2, "ID": 2}
    assert calls["create"] == 1

    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 2


def test_update_uses_id_path_and_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "update": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])
        if method == "PUT" and url.endswith("/listaPrecioBean/1"):
            calls["update"] += 1
            return httpx.Response(
                200, json={"codigo": "LP1", "id": 1, "ID": 1, "nombre": "LP1-upd"}
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 1

    updated = gw.update(1, {"nombre": "LP1-upd"})
    assert updated == {"codigo": "LP1", "id": 1, "ID": 1, "nombre": "LP1-upd"}
    assert calls["update"] == 1

    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 2


def test_delete_uses_id_path_and_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "delete": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])
        if method == "DELETE" and url.endswith("/listaPrecioBean/1"):
            calls["delete"] += 1
            return httpx.Response(200, json={})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 1

    assert gw.delete(1) is True
    assert calls["delete"] == 1

    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 2


def test_patch_uses_id_path_and_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "patch": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP1", "id": 1, "ID": 1}])
        if method == "PATCH" and url.endswith("/listaPrecioBean/1"):
            calls["patch"] += 1
            return httpx.Response(
                200,
                json={
                    "codigo": "LP1",
                    "id": 1,
                    "ID": 1,
                    "descripcion": "Actualizada por PATCH",
                },
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 1

    patched = gw.patch(1, {"descripcion": "Actualizada por PATCH"})
    assert patched == {
        "codigo": "LP1",
        "id": 1,
        "ID": 1,
        "descripcion": "Actualizada por PATCH",
    }
    assert calls["patch"] == 1

    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 2
