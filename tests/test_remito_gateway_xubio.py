import httpx
import pytest

import src.infrastructure.httpx.remito_gateway_xubio as remito_gateway
from src.infrastructure.httpx.remito_gateway_xubio import XubioRemitoGateway
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    remito_gateway._GLOBAL_LIST_CACHE.clear()
    remito_gateway._GLOBAL_ITEM_CACHE.clear()
    yield
    remito_gateway._GLOBAL_LIST_CACHE.clear()
    remito_gateway._GLOBAL_ITEM_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"transaccionId": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway()
    assert gw.list() == [{"transaccionId": 1}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json={"items": [{"transaccionId": 2}]})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway()
    assert gw.list() == [{"transaccionId": 2}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"transaccionId": 1}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway(list_cache_ttl=60)
    assert gw.list() == [{"transaccionId": 1}]
    assert gw.list() == [{"transaccionId": 1}]
    assert calls["count"] == 1


def test_create_invalidates_list_cache(monkeypatch):
    calls = {"list": 0, "create": 0}

    def fake_request(method, url, **_kwargs):
        if method == "GET" and url.endswith("/remitoVentaBean"):
            calls["list"] += 1
            return httpx.Response(200, json=[{"transaccionId": 1}])
        if method == "POST" and url.endswith("/remitoVentaBean"):
            calls["create"] += 1
            return httpx.Response(200, json={"transaccionId": 2})
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway(list_cache_ttl=60)
    assert gw.list() == [{"transaccionId": 1}]
    assert gw.list() == [{"transaccionId": 1}]
    assert calls["list"] == 1
    assert gw.create({"numeroRemito": "A-0001-00000001"}) == {"transaccionId": 2}
    assert calls["create"] == 1
    assert gw.list() == [{"transaccionId": 1}]
    assert calls["list"] == 2


def test_update_uses_swagger_put_path_and_body_transaccion_id(monkeypatch):
    captured = {}

    def fake_request(method, url, **kwargs):
        captured["method"] = method
        captured["url"] = url
        captured["json"] = kwargs.get("json")
        return httpx.Response(200, json={"transaccionId": 7, "numeroRemito": "R-2"})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioRemitoGateway()

    updated = gw.update(7, {"transaccionId": 999, "numeroRemito": "R-2"})

    assert updated == {"transaccionId": 7, "numeroRemito": "R-2"}
    assert captured["method"] == "PUT"
    assert captured["url"].endswith("/remitoVentaBean")
    assert captured["json"]["transaccionId"] == 7


def test_prod_mode_disables_get_cache(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"transaccionId": 5}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    monkeypatch.setenv("IS_PROD", "true")

    gw = XubioRemitoGateway()
    assert gw.list() == [{"transaccionId": 5}]
    assert gw.list() == [{"transaccionId": 5}]
    assert calls["count"] == 2


def test_get_uses_item_cache_without_http_calls(monkeypatch):
    gw = XubioRemitoGateway(list_cache_ttl=60)
    gw._store_item_cache(9, {"transaccionId": 9, "numeroRemito": "R-9"})

    monkeypatch.setattr(
        remito_gateway,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(9) == {"transaccionId": 9, "numeroRemito": "R-9"}


def test_get_uses_list_cache_without_http_calls(monkeypatch):
    gw = XubioRemitoGateway(list_cache_ttl=60)
    gw._store_cache([{"transaccionId": 10, "numeroRemito": "R-10"}])

    monkeypatch.setattr(
        remito_gateway,
        "request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(10) == {"transaccionId": 10, "numeroRemito": "R-10"}


def test_get_returns_none_on_404(monkeypatch):
    monkeypatch.setattr(
        remito_gateway,
        "request_with_token",
        lambda *_args, **_kwargs: httpx.Response(404, json={}),
    )

    gw = XubioRemitoGateway()
    assert gw.get(99) is None


def test_get_falls_back_to_list_on_5xx(monkeypatch):
    def fake_detail(_method, _url, **_kwargs):
        return httpx.Response(500, text="boom")

    def fake_list(_method, _url, **_kwargs):
        return httpx.Response(200, json=[{"transaccionId": 33}])

    monkeypatch.setattr(remito_gateway, "request_with_token", fake_detail)
    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token", fake_list
    )

    gw = XubioRemitoGateway()
    assert gw.get(33) == {"transaccionId": 33}


def test_get_wraps_http_error(monkeypatch):
    request = httpx.Request("GET", "https://xubio.local")

    def boom(*_args, **_kwargs):
        raise httpx.ConnectError("boom", request=request)

    monkeypatch.setattr(remito_gateway, "request_with_token", boom)

    gw = XubioRemitoGateway()
    with pytest.raises(ExternalServiceError):
        gw.get(1)


def test_delete_invalidates_cache_only_when_deleted(monkeypatch):
    gw = XubioRemitoGateway(list_cache_ttl=60)
    gw._store_cache([{"transaccionId": 1}])
    gw._store_item_cache(1, {"transaccionId": 1})

    monkeypatch.setattr(remito_gateway, "delete_item", lambda **_kwargs: True)
    assert gw.delete(1) is True
    assert remito_gateway._GLOBAL_LIST_CACHE == {}
    assert remito_gateway._GLOBAL_ITEM_CACHE == {}

    gw._store_cache([{"transaccionId": 2}])
    gw._store_item_cache(2, {"transaccionId": 2})
    monkeypatch.setattr(remito_gateway, "delete_item", lambda **_kwargs: False)
    assert gw.delete(2) is False
    assert remito_gateway._GLOBAL_LIST_CACHE
    assert remito_gateway._GLOBAL_ITEM_CACHE
