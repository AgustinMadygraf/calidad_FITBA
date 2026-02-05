import pytest

httpx = pytest.importorskip("httpx")

from servidor.app import main as app_main


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_health(monkeypatch):
    monkeypatch.setattr(app_main.conn_factory, "ensure_schema", lambda _: None)
    app = app_main.create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.anyio
async def test_startup_calls_ensure_schema(monkeypatch):
    called = {"ok": False}

    def _ensure_schema(path):
        called["ok"] = True

    monkeypatch.setattr(app_main.conn_factory, "ensure_schema", _ensure_schema)
    app = app_main.create_app()
    await app.router.startup()
    assert called["ok"] is True
    await app.router.shutdown()
