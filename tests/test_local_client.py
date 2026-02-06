from __future__ import annotations

import httpx
import pytest

from src.client.app.local_xubio_client import LocalXubioClient


def _response(status_code: int, payload: dict, url: str) -> httpx.Response:
    request = httpx.Request("GET", url)
    return httpx.Response(status_code, json=payload, request=request)


def test_local_client_request_error(monkeypatch) -> None:
    client = LocalXubioClient("http://localhost:9999")

    def fake_request(*args, **kwargs):
        _ = (args, kwargs)
        raise httpx.RequestError("boom", request=httpx.Request("GET", "http://localhost"))

    monkeypatch.setattr(client._client, "request", fake_request)

    with pytest.raises(RuntimeError, match="No se pudo conectar al servidor local"):
        client.list_products()


def test_local_client_http_status_error(monkeypatch) -> None:
    client = LocalXubioClient("http://localhost:9999")

    def fake_request(*args, **kwargs):
        _ = (args, kwargs)
        return _response(404, {"detail": "No encontrado"}, "http://localhost/API/1.1/ProductoVentaBean")

    monkeypatch.setattr(client._client, "request", fake_request)

    with pytest.raises(RuntimeError, match="Servidor local respondio HTTP 404: No encontrado."):
        client.list_products()
