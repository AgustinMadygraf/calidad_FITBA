from __future__ import annotations

import runpy

import src.client.app.main as client_main


def test_client_entrypoint_calls_app(monkeypatch) -> None:
    called = {"count": 0}

    def fake_app() -> None:
        called["count"] += 1

    monkeypatch.setattr(client_main, "app", fake_app)
    runpy.run_module("src.client.app.__main__", run_name="__main__")
    assert called["count"] == 1


def test_server_entrypoint_calls_uvicorn(monkeypatch) -> None:
    import uvicorn

    called = {"args": None, "kwargs": None}

    def fake_run(*args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs

    monkeypatch.setattr(uvicorn, "run", fake_run)
    runpy.run_module("src.server.app.__main__", run_name="__main__")

    assert called["args"]
    assert called["kwargs"]["host"] == "0.0.0.0"
