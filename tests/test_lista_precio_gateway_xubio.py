import httpx
import pytest

import src.infrastructure.httpx.lista_precio_gateway_xubio as lista_precio_gateway
from src.infrastructure.httpx.lista_precio_gateway_xubio import XubioListaPrecioGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    lista_precio_gateway._GLOBAL_LIST_CACHE.clear()
    lista_precio_gateway._GLOBAL_ITEM_CACHE.clear()
    yield
    lista_precio_gateway._GLOBAL_LIST_CACHE.clear()
    lista_precio_gateway._GLOBAL_ITEM_CACHE.clear()


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


def test_get_uses_detail_endpoint_first(monkeypatch):
    calls = {"detail": 0, "list": 0}
    detail_payload = {
        "listaPrecioID": 2,
        "nombre": "LP2",
        "descripcion": "detalle completo",
        "listaPrecioItem": [{"producto": {"id": 10}, "precio": 100}],
    }

    def fake_request(_method, url, **_kwargs):
        if url.endswith("/listaPrecioBean/2"):
            calls["detail"] += 1
            return httpx.Response(200, json=detail_payload)
        if url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP2", "id": 2, "ID": 2}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.get(2) == detail_payload
    assert calls["detail"] == 1
    assert calls["list"] == 0


def test_get_falls_back_to_list_on_5xx(monkeypatch):
    calls = {"detail": 0, "list": 0}

    def fake_request(_method, url, **_kwargs):
        if url.endswith("/listaPrecioBean/2"):
            calls["detail"] += 1
            return httpx.Response(500, text="boom")
        if url.endswith("/listaPrecioBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"codigo": "LP2", "id": 2, "ID": 2}])
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    assert gw.get(2) == {"codigo": "LP2", "id": 2, "ID": 2}
    assert calls["detail"] == 1
    assert calls["list"] == 1


def test_get_returns_none_on_detail_404_without_list_fallback(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/listaPrecioBean/2"):
            return httpx.Response(404)
        if url.endswith("/listaPrecioBean"):
            raise AssertionError("No debe consultar lista cuando detalle devuelve 404")
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioListaPrecioGateway()
    assert gw.get(2) is None


def test_get_uses_item_cache_without_http_calls(monkeypatch):
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    gw._store_item_cache(2, {"listaPrecioID": 2, "nombre": "LP2"})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(2) == {"listaPrecioID": 2, "nombre": "LP2"}


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
    gw._store_item_cache(1, {"listaPrecioID": 1, "nombre": "LP1"})

    assert gw.create({"nombre": "LP2"}) == {"codigo": "LP2", "id": 2, "ID": 2}
    assert calls["create"] == 1
    assert lista_precio_gateway._GLOBAL_ITEM_CACHE == {}

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
    gw._store_item_cache(1, {"listaPrecioID": 1, "nombre": "LP1"})

    updated = gw.update(1, {"nombre": "LP1-upd"})
    assert updated == {"codigo": "LP1", "id": 1, "ID": 1, "nombre": "LP1-upd"}
    assert calls["update"] == 1
    assert lista_precio_gateway._GLOBAL_ITEM_CACHE == {}

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
    gw._store_item_cache(1, {"listaPrecioID": 1, "nombre": "LP1"})

    assert gw.delete(1) is True
    assert calls["delete"] == 1
    assert lista_precio_gateway._GLOBAL_ITEM_CACHE == {}

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
    gw._store_item_cache(1, {"listaPrecioID": 1, "nombre": "LP1"})

    patched = gw.patch(1, {"descripcion": "Actualizada por PATCH"})
    assert patched == {
        "codigo": "LP1",
        "id": 1,
        "ID": 1,
        "descripcion": "Actualizada por PATCH",
    }
    assert calls["patch"] == 1
    assert lista_precio_gateway._GLOBAL_ITEM_CACHE == {}

    assert gw.list() == [{"codigo": "LP1", "id": 1, "ID": 1}]
    assert calls["list"] == 2


def test_delete_keeps_cache_when_resource_not_deleted(monkeypatch):
    gw = XubioListaPrecioGateway(list_cache_ttl=60)
    gw._store_cache([{"listaPrecioID": 2, "nombre": "LP2"}])
    gw._store_item_cache(2, {"listaPrecioID": 2, "nombre": "LP2"})

    monkeypatch.setattr(lista_precio_gateway, "delete_item", lambda **_kwargs: False)

    assert gw.delete(2) is False
    assert lista_precio_gateway._GLOBAL_LIST_CACHE
    assert lista_precio_gateway._GLOBAL_ITEM_CACHE
