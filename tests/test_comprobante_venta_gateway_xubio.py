import httpx
import pytest

import src.infrastructure.httpx.comprobante_venta_gateway_xubio as comprobante_gateway
from src.infrastructure.httpx.comprobante_venta_gateway_xubio import (
    XubioComprobanteVentaGateway,
)
from src.use_cases.errors import ExternalServiceError


@pytest.fixture(autouse=True)
def reset_cache():
    comprobante_gateway._GLOBAL_LIST_CACHE.clear()
    comprobante_gateway._GLOBAL_ITEM_CACHE.clear()
    yield
    comprobante_gateway._GLOBAL_LIST_CACHE.clear()
    comprobante_gateway._GLOBAL_ITEM_CACHE.clear()


def test_list_accepts_list_payload(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(200, json=[{"transaccionid": 1, "nombre": "FV1"}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway()
    assert gw.list() == [{"transaccionid": 1, "nombre": "FV1"}]


def test_list_accepts_items_wrapper(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(
            200,
            json={"items": [{"transaccionid": 2, "nombre": "FV2"}]},
        )

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway()
    assert gw.list() == [{"transaccionid": 2, "nombre": "FV2"}]


def test_list_raises_on_error_status(monkeypatch):
    def fake_request(*_args, **_kwargs):
        return httpx.Response(500, text="boom")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway()
    with pytest.raises(ExternalServiceError):
        gw.list()


def test_get_uses_detail_endpoint_first(monkeypatch):
    calls = {"detail": 0, "list": 0}
    detail_payload = {"transaccionid": 2, "nombre": "FV2", "importetotal": 123.0}

    def fake_request(_method, url, **_kwargs):
        if url.endswith("/comprobanteVentaBean/2"):
            calls["detail"] += 1
            return httpx.Response(200, json=detail_payload)
        if url.endswith("/comprobanteVentaBean"):
            calls["list"] += 1
            return httpx.Response(
                200, json=[{"transaccionid": 2, "nombre": "FV2-min"}]
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway(list_cache_ttl=60)
    assert gw.get(2) == detail_payload
    assert calls["detail"] == 1
    assert calls["list"] == 0


def test_get_falls_back_to_list_on_5xx(monkeypatch):
    calls = {"detail": 0, "list": 0}

    def fake_request(_method, url, **_kwargs):
        if url.endswith("/comprobanteVentaBean/2"):
            calls["detail"] += 1
            return httpx.Response(500, text="boom")
        if url.endswith("/comprobanteVentaBean"):
            calls["list"] += 1
            return httpx.Response(
                200, json=[{"transaccionid": 2, "nombre": "FV2-min"}]
            )
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway(list_cache_ttl=60)
    assert gw.get(2) == {"transaccionid": 2, "nombre": "FV2-min"}
    assert calls["detail"] == 1
    assert calls["list"] == 1


def test_get_returns_none_on_detail_404_without_list_fallback(monkeypatch):
    def fake_request(_method, url, **_kwargs):
        if url.endswith("/comprobanteVentaBean/2"):
            return httpx.Response(404)
        if url.endswith("/comprobanteVentaBean"):
            raise AssertionError("No debe consultar lista cuando detalle devuelve 404")
        return httpx.Response(404)

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway()
    assert gw.get(2) is None


def test_get_uses_item_cache_without_http_calls(monkeypatch):
    gw = XubioComprobanteVentaGateway(list_cache_ttl=60)
    gw._store_item_cache(2, {"transaccionid": 2, "nombre": "FV2"})

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("No debe llamar HTTP")
        ),
    )

    assert gw.get(2) == {"transaccionid": 2, "nombre": "FV2"}


def test_list_uses_cache_within_ttl(monkeypatch):
    calls = {"count": 0}

    def fake_request(*_args, **_kwargs):
        calls["count"] += 1
        return httpx.Response(200, json=[{"transaccionid": 1, "nombre": "FV1"}])

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )
    gw = XubioComprobanteVentaGateway(list_cache_ttl=60)
    assert gw.list() == [{"transaccionid": 1, "nombre": "FV1"}]
    assert gw.list() == [{"transaccionid": 1, "nombre": "FV1"}]
    assert calls["count"] == 1
