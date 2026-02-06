from __future__ import annotations

from shared.schemas import ProductOut
from server.infrastructure.clients.real_xubio_api_client import RealXubioApiClient


def test_xubio_like_product_crud(client) -> None:
    create_resp = client.post(
        "/API/1.1/ProductoVentaBean",
        json={
            "productoid": "p-100",
            "nombre": "Producto Replica",
            "codigo": "SKU-100",
            "precioVenta": 25.5,
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["productoid"] == "p-100"
    assert created["nombre"] == "Producto Replica"

    list_resp = client.get("/API/1.1/ProductoVentaBean")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(item["productoid"] == "p-100" for item in items)

    patch_resp = client.patch(
        "/API/1.1/ProductoVentaBean/p-100",
        json={"nombre": "Producto Actualizado"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["nombre"] == "Producto Actualizado"

    get_resp = client.get("/API/1.1/ProductoVentaBean/p-100")
    assert get_resp.status_code == 200
    assert get_resp.json()["nombre"] == "Producto Actualizado"

    delete_resp = client.delete("/API/1.1/ProductoVentaBean/p-100")
    assert delete_resp.status_code == 204


def test_sync_pull_from_real_xubio_to_local_replica(client, monkeypatch) -> None:
    def _fake_list_products(self, limit: int = 50, offset: int = 0):
        _ = (self, limit, offset)
        return [
            ProductOut(
                external_id="sync-1",
                name="Producto Sync",
                sku="SYNC",
                price=123.0,
            )
        ]

    monkeypatch.setattr(RealXubioApiClient, "list_products", _fake_list_products)

    sync_resp = client.post("/sync/pull/product/from-xubio")
    assert sync_resp.status_code == 200
    assert sync_resp.json()["status"] == "ok"

    list_resp = client.get("/API/1.1/ProductoVentaBean")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(item["productoid"] == "sync-1" and item["nombre"] == "Producto Sync" for item in items)
