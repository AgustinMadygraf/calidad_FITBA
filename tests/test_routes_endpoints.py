from __future__ import annotations

from src.interface_adapter.controller.api.app.settings import settings as server_settings

def test_routes_not_found_paths(client) -> None:
    get_resp = client.get("/API/1.1/ProductoVentaBean/does-not-exist")
    assert get_resp.status_code == 404

    patch_resp = client.patch("/API/1.1/ProductoVentaBean/does-not-exist", json={"nombre": "X"})
    assert patch_resp.status_code == 404

    delete_resp = client.delete("/API/1.1/ProductoVentaBean/does-not-exist")
    assert delete_resp.status_code == 404


def test_sync_pull_product_mock_route(client) -> None:
    resp = client.post("/sync/pull/product")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_sync_pull_from_xubio_error(monkeypatch, client) -> None:
    import src.interface_adapter.controller.api.routes as routes

    class _FakeSync:
        def __init__(self, *args, **kwargs):
            _ = (args, kwargs)

        def execute(self, is_mock: bool):
            _ = is_mock
            return {"status": "error", "detail": "fallo"}

    monkeypatch.setattr(routes, "SyncPullProduct", _FakeSync)

    resp = client.post("/sync/pull/product/from-xubio")
    assert resp.status_code == 502


def test_sync_push_product_prod_branch(monkeypatch) -> None:
    class _FakeClient:
        def __init__(self) -> None:
            self.updated = 0

        def update_product(self, external_id, payload):
            _ = external_id
            self.updated += 1
            return payload

    fake = _FakeClient()
    import src.interface_adapter.controller.api.routes as routes

    monkeypatch.setattr(server_settings, "IS_PROD", True)
    monkeypatch.setattr(routes.settings, "IS_PROD", True)
    monkeypatch.setattr(routes, "get_xubio_client", lambda db: fake)

    from src.infrastructure.db.session import SessionLocal
    from src.infrastructure.repositories.integration_record_repository import (
        ProductRepository,
    )

    db = SessionLocal()
    try:
        repo = ProductRepository(db)
        repo.create("p-1", {"productoid": "p-1", "nombre": "A"})
        repo.create("p-2", {"productoid": "p-2", "nombre": "B"})
        repo.create("p-3", {"productoid": "p-3", "nombre": "C"})

        result = routes.sync_push_product(db=db)
        assert result["status"] == "ok"
    finally:
        db.close()

    assert fake.updated == 3
