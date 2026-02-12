import pathlib
import runpy
import warnings
from typing import Any, Dict

import pytest
import uvicorn
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.infrastructure.fastapi import api
from src.infrastructure.fastapi.api import app


@pytest.mark.parametrize(
    "path,handler_name,payload",
    [
        ("/API/1.1/clienteBean/1", "get_cliente", {"clienteid": 1, "nombre": "ACME"}),
        (
            "/API/1.1/remitoVentaBean/1",
            "get_remito",
            {"transaccionId": 1, "numeroRemito": "R-1"},
        ),
        (
            "/API/1.1/ProductoVentaBean/1",
            "get_producto",
            {"productoid": 1, "nombre": "P1"},
        ),
        (
            "/API/1.1/ProductoCompraBean/1",
            "get_producto",
            {"productoid": 1, "nombre": "PC1"},
        ),
        ("/API/1.1/depositos/1", "get_deposito", {"id": 1, "nombre": "D1"}),
    ],
)
def test_get_routes_return_payload_on_success(
    monkeypatch, path: str, handler_name: str, payload: Dict[str, Any]
):
    monkeypatch.setenv("IS_PROD", "false")
    monkeypatch.setattr(api.handlers, handler_name, lambda *_args, **_kwargs: payload)
    client = TestClient(app)
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == payload


@pytest.mark.parametrize(
    "path,handler_name,payload",
    [
        (
            "/API/1.1/clienteBean/1",
            "update_cliente",
            {"clienteid": 1, "nombre": "ACME-OK"},
        ),
        (
            "/API/1.1/ProductoVentaBean/1",
            "update_producto",
            {"productoid": 1, "nombre": "P1-OK"},
        ),
    ],
)
def test_put_routes_return_payload_on_success(
    monkeypatch, path: str, handler_name: str, payload: Dict[str, Any]
):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, handler_name, lambda *_args, **_kwargs: payload)
    client = TestClient(app)
    response = client.put(path, json={})
    assert response.status_code == 200
    assert response.json() == payload


@pytest.mark.parametrize(
    "path,expected_key,expected_value,handler_name",
    [
        ("/API/1.1/clienteBean/7", "cliente_id", 7, "delete_cliente"),
        ("/API/1.1/remitoVentaBean/7", "transaccionId", 7, "delete_remito"),
        ("/API/1.1/ProductoVentaBean/7", "productoid", 7, "delete_producto"),
    ],
)
def test_delete_routes_return_deleted_payload_on_success(
    monkeypatch,
    path: str,
    expected_key: str,
    expected_value: int,
    handler_name: str,
):
    monkeypatch.setenv("IS_PROD", "true")
    monkeypatch.setattr(api.handlers, handler_name, lambda *_args, **_kwargs: True)
    client = TestClient(app)
    response = client.delete(path)
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    assert response.json()[expected_key] == expected_value


def test_module_exec_covers_missing_frontend_and_main_branch(monkeypatch):
    from src.infrastructure.fastapi import app as app_module

    called: Dict[str, Any] = {}
    original_exists = pathlib.Path.exists

    def fake_exists(self: pathlib.Path) -> bool:
        if self.name == "frontend" and str(self).endswith("/calidad_FITBA/frontend"):
            return False
        return original_exists(self)

    monkeypatch.setattr(pathlib.Path, "exists", fake_exists)
    monkeypatch.setattr(
        uvicorn,
        "run",
        lambda *args, **kwargs: called.update({"args": args, "kwargs": kwargs}),
    )
    monkeypatch.setattr(app_module, "app", FastAPI())

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        runpy.run_module("src.infrastructure.fastapi.api", run_name="__main__")

    assert called["args"] == ("src.infrastructure.fastapi.api:app",)
    assert called["kwargs"]["reload"] is True
