from __future__ import annotations

from typing import Any

import httpx
import pytest

from src.interface_adapter.controller.cli.real_xubio_client import RealXubioClient
from src.interface_adapter.gateways.real_xubio_api_client import RealXubioApiClient
from src.interface_adapter.controller.api.app.settings import settings as server_settings
from src.entities.schemas import ProductCreate, ProductUpdate


def _response(status_code: int, payload: Any, url: str = "https://xubio.com/API/1.1/ProductoVentaBean") -> httpx.Response:
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=payload, request=request)


def test_server_real_client_token_refresh(monkeypatch) -> None:
    client = RealXubioApiClient()
    monkeypatch.setattr(server_settings, "xubio_client_id", "id")
    monkeypatch.setattr(server_settings, "xubio_secret_id", "secret")
    calls = {"request": 0, "token": 0}

    def fake_post(*args, **kwargs):
        _ = (args, kwargs)
        calls["token"] += 1
        return _response(200, {"access_token": f"t{calls['token']}"}, url="https://xubio.com/API/1.1/TokenEndpoint")

    def fake_request(method, url, headers=None, **kwargs):
        _ = (method, url, headers, kwargs)
        calls["request"] += 1
        if calls["request"] == 1:
            return _response(401, {"error": "invalid_token"})
        return _response(200, {"ok": True})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(client._client, "request", fake_request)

    response = client._request("GET", "/ProductoVentaBean")
    assert response.status_code == 200
    assert calls["request"] == 2
    assert calls["token"] == 2


def test_server_real_client_map_product() -> None:
    client = RealXubioApiClient()
    mapped = client._map_product(
        {"productoid": 10, "nombre": "Nombre", "codigo": "SKU", "precioVenta": 99.0}
    )
    assert mapped.external_id == "10"
    assert mapped.name == "Nombre"
    assert mapped.sku == "SKU"
    assert mapped.price == 99.0


def test_server_real_client_missing_credentials(monkeypatch) -> None:
    client = RealXubioApiClient()
    monkeypatch.setattr(server_settings, "xubio_client_id", None)
    monkeypatch.setattr(server_settings, "xubio_secret_id", None)
    try:
        client._get_token()
    except ValueError as exc:
        assert "Faltan" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_server_real_client_is_invalid_token_false() -> None:
    client = RealXubioApiClient()
    response = _response(200, {"ok": True})
    assert client._is_invalid_token(response) is False


def test_server_real_client_methods(monkeypatch) -> None:
    client = RealXubioApiClient()
    monkeypatch.setattr(server_settings, "xubio_client_id", "id")
    monkeypatch.setattr(server_settings, "xubio_secret_id", "secret")

    def fake_get_token():
        return "token"

    def fake_request(method, url, headers=None, **kwargs):
        _ = (headers, kwargs)
        if method == "GET" and url.endswith("/ProductoVentaBean"):
            return _response(200, [{"productoid": "p-1", "nombre": "A"}])
        if method == "GET":
            return _response(200, {"external_id": "p-2", "name": "B"})
        if method == "POST":
            return _response(200, {"external_id": "p-3", "name": "C"})
        if method == "PATCH":
            return _response(200, {"external_id": "p-4", "name": "D"})
        return _response(204, {}, url="https://xubio.com/API/1.1/ProductoVentaBean/p-5")

    monkeypatch.setattr(client, "_get_token", fake_get_token)
    monkeypatch.setattr(client._client, "request", fake_request)

    assert client.list_products()[0].external_id == "p-1"
    assert client.get_product("p-2").external_id == "p-2"
    assert client.create_product(ProductCreate(external_id="p-3", name="X")).external_id == "p-3"
    assert client.update_product("p-4", ProductUpdate(name="Y")).external_id == "p-4"
    assert client.delete_product("p-5") is None


def test_client_real_client_token_refresh(monkeypatch) -> None:
    client = RealXubioClient("id", "secret")
    calls = {"request": 0, "token": 0}

    def fake_post(*args, **kwargs):
        _ = (args, kwargs)
        calls["token"] += 1
        return _response(200, {"access_token": f"t{calls['token']}"}, url="https://xubio.com/API/1.1/TokenEndpoint")

    def fake_request(method, url, headers=None, **kwargs):
        _ = (method, url, headers, kwargs)
        calls["request"] += 1
        if calls["request"] == 1:
            return _response(401, {"error": "invalid_token"})
        return _response(200, [{"productoid": "p-1"}])

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setattr(client._client, "request", fake_request)

    items = client.list_products()
    assert items[0]["productoid"] == "p-1"
    assert calls["request"] == 2
    assert calls["token"] == 2


def test_client_real_client_get_token_missing(monkeypatch) -> None:
    client = RealXubioClient("id", "secret")

    def fake_post(*args, **kwargs):
        _ = (args, kwargs)
        return _response(200, {"nope": "x"}, url="https://xubio.com/API/1.1/TokenEndpoint")

    monkeypatch.setattr(httpx, "post", fake_post)
    with pytest.raises(ValueError):
        client._get_token()


def test_client_real_client_is_invalid_token_false() -> None:
    client = RealXubioClient("id", "secret")
    response = _response(200, {"ok": True})
    assert client._is_invalid_token(response) is False


def test_client_real_client_is_invalid_token_bad_json() -> None:
    client = RealXubioClient("id", "secret")
    request = httpx.Request("GET", "https://xubio.com/API/1.1/ProductoVentaBean")
    response = httpx.Response(401, content=b"not-json", request=request)
    assert client._is_invalid_token(response) is False


def test_client_real_client_methods(monkeypatch) -> None:
    client = RealXubioClient("id", "secret")

    def fake_get_token():
        return "token"

    def fake_request(method, url, headers=None, **kwargs):
        _ = (headers, kwargs)
        if method == "GET" and url.endswith("/ProductoVentaBean"):
            return _response(200, [{"productoid": "p-1"}])
        if method == "GET":
            return _response(200, {"productoid": "p-2"})
        if method == "POST":
            return _response(200, {"productoid": "p-3"})
        if method == "PATCH":
            return _response(200, {"productoid": "p-4"})
        return _response(204, {}, url="https://xubio.com/API/1.1/ProductoVentaBean/p-5")

    monkeypatch.setattr(client, "_get_token", fake_get_token)
    monkeypatch.setattr(client._client, "request", fake_request)

    assert client.list_products()[0]["productoid"] == "p-1"
    assert client.get_product("p-2")["productoid"] == "p-2"
    assert client.create_product({"nombre": "A"})["productoid"] == "p-3"
    assert client.update_product("p-4", {"nombre": "B"})["productoid"] == "p-4"
    assert client.delete_product("p-5") is None
