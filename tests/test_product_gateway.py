from __future__ import annotations

from src.client.app.product_gateway import (
    LocalFastApiProductGateway,
    XubioDirectProductGateway,
    map_product_screen,
)


def test_map_product_screen_formats() -> None:
    screen = map_product_screen(
        {"productoid": "p-1", "nombre": "  Producto   X  ", "codigo": "SKU", "precioVenta": 12.5}
    )
    assert "Producto:" in screen
    assert "ID: p-1" in screen
    assert "Nombre: Producto X" in screen
    assert "SKU: SKU" in screen
    assert "Precio: 12.5" in screen


def test_local_gateway_list_and_sync(monkeypatch) -> None:
    gateway = LocalFastApiProductGateway("http://localhost:8000")

    def fake_list():
        return [
            {"productoid": "p-1", "nombre": "Prod 1"},
            {"productoid": "p-2", "nombre": "Prod 2"},
        ]

    def fake_sync():
        return {"status": "ok"}

    monkeypatch.setattr(gateway._client, "list_products", fake_list)
    monkeypatch.setattr(gateway._client, "sync_pull_from_xubio", fake_sync)

    listing = gateway.list(session_id="s")
    assert "Productos:" in listing
    assert "- p-1 | Prod 1" in listing

    sync = gateway.sync_pull(session_id="s")
    assert "Sync pull OK" in sync


def test_real_gateway_no_sync(monkeypatch) -> None:
    gateway = XubioDirectProductGateway("id", "secret")
    monkeypatch.setattr(gateway._client, "list_products", lambda: [])
    assert gateway.sync_pull(session_id="s") == "No disponible en modo real desde el cliente."


def test_gateway_render_menu_and_empty_list(monkeypatch) -> None:
    local_gateway = LocalFastApiProductGateway("http://localhost:8000")
    real_gateway = XubioDirectProductGateway("id", "secret")

    assert "Alta" in local_gateway.render_menu("s")
    assert "Alta" in real_gateway.render_menu("s")

    monkeypatch.setattr(local_gateway._client, "list_products", lambda: [])
    monkeypatch.setattr(real_gateway._client, "list_products", lambda: [])

    assert local_gateway.list(session_id="s") == "Sin productos."
    assert real_gateway.list(session_id="s") == "Sin productos."
