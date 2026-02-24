import run
import pytest


def test_resolve_bind_port_uses_preferred_when_available(monkeypatch):
    monkeypatch.setattr(run, "_ensure_port_available", lambda host, port: None)
    assert run._resolve_bind_port("127.0.0.1", 8000, max_tries=3) == 8000


def test_resolve_bind_port_falls_forward(monkeypatch):
    busy = {8000, 8001}

    def fake_ensure(_host, port):
        if port in busy:
            raise RuntimeError("occupied")

    monkeypatch.setattr(run, "_ensure_port_available", fake_ensure)
    assert run._resolve_bind_port("127.0.0.1", 8000, max_tries=5) == 8002


def test_resolve_bind_port_raises_when_all_busy(monkeypatch):
    monkeypatch.setattr(
        run, "_ensure_port_available", lambda host, port: (_ for _ in ()).throw(RuntimeError("occupied"))
    )
    with pytest.raises(RuntimeError, match="No se encontro puerto disponible"):
        run._resolve_bind_port("127.0.0.1", 8000, max_tries=1)
