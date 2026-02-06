from __future__ import annotations

from src.client.app.product_gateway import LocalFastApiProductGateway, XubioDirectProductGateway


def test_local_gateway_actions(monkeypatch) -> None:
    gateway = LocalFastApiProductGateway("http://localhost:8000")

    monkeypatch.setattr(gateway._client, "create_product", lambda payload: payload | {"productoid": "p-1"})
    monkeypatch.setattr(gateway._client, "update_product", lambda external_id, payload: {"productoid": external_id, **payload})
    monkeypatch.setattr(gateway._client, "get_product", lambda external_id: {"productoid": external_id, "nombre": "Prod"})
    monkeypatch.setattr(gateway._client, "delete_product", lambda external_id: None)

    assert "ID: p-1" in gateway.create(session_id="s", external_id="p-1", name="Prod", sku="S", price=1.0)
    assert "ID: p-2" in gateway.update(session_id="s", external_id="p-2", name="N", sku=None, price=None)
    assert "ID: p-3" in gateway.get(session_id="s", external_id="p-3")
    assert gateway.delete(session_id="s", external_id="p-4") == "Producto eliminado."


def test_real_gateway_actions(monkeypatch) -> None:
    gateway = XubioDirectProductGateway("id", "secret")

    monkeypatch.setattr(gateway._client, "create_product", lambda payload: payload | {"productoid": "p-1"})
    monkeypatch.setattr(gateway._client, "update_product", lambda external_id, payload: {"productoid": external_id, **payload})
    monkeypatch.setattr(gateway._client, "get_product", lambda external_id: {"productoid": external_id, "nombre": "Prod"})
    monkeypatch.setattr(gateway._client, "delete_product", lambda external_id: None)

    assert "ID: p-1" in gateway.create(session_id="s", external_id="p-1", name="Prod", sku="S", price=1.0)
    assert "ID: p-2" in gateway.update(session_id="s", external_id="p-2", name="N", sku=None, price=None)
    assert "ID: p-3" in gateway.get(session_id="s", external_id="p-3")
    assert gateway.delete(session_id="s", external_id="p-4") == "Producto eliminado."
