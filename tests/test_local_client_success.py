from __future__ import annotations

import httpx

from src.client.app.local_xubio_client import LocalXubioClient


def _response(status_code: int, payload: dict, url: str) -> httpx.Response:
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=payload, request=request)


def test_local_client_success_paths(monkeypatch) -> None:
    client = LocalXubioClient("http://localhost:8000")

    def fake_request(method, url, **kwargs):
        _ = (method, kwargs)
        return _response(200, {"ok": True, "url": url}, f"http://localhost{url}")

    monkeypatch.setattr(client._client, "request", fake_request)
    monkeypatch.setattr(client._sync_client, "request", fake_request)

    assert client.list_products()["ok"] is True
    assert client.get_product("p-1")["url"].endswith("/ProductoVentaBean/p-1")
    assert client.create_product({"nombre": "A"})["ok"] is True
    assert client.update_product("p-2", {"nombre": "B"})["ok"] is True
    assert client.delete_product("p-3") is None
    assert client.sync_pull_from_xubio()["ok"] is True
