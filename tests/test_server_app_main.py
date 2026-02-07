from __future__ import annotations

import anyio

import src.interface_adapter.controller.api.app.main as main_module


def test_lifespan_creates_tables(monkeypatch) -> None:
    called = {"count": 0}

    def fake_create_all(bind):
        _ = bind
        called["count"] += 1

    monkeypatch.setattr(main_module.Base.metadata, "create_all", fake_create_all)
    async def _run():
        async with main_module._lifespan(main_module.app):
            pass

    anyio.run(_run)
    assert called["count"] == 1
