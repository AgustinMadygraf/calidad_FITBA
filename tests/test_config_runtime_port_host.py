import pytest

from src.shared import config


def test_get_host_uses_env_override(monkeypatch):
    monkeypatch.setenv("APP_HOST", "127.0.0.1")
    assert config.get_host() == "127.0.0.1"


def test_get_port_uses_env_override(monkeypatch):
    monkeypatch.setenv("APP_PORT", "9001")
    assert config.get_port() == 9001


def test_get_port_rejects_non_integer(monkeypatch):
    monkeypatch.setenv("APP_PORT", "abc")
    with pytest.raises(ValueError, match="APP_PORT debe ser un entero valido"):
        config.get_port()


def test_get_port_rejects_out_of_range(monkeypatch):
    monkeypatch.setenv("APP_PORT", "70000")
    with pytest.raises(ValueError, match="APP_PORT debe estar entre 1 y 65535"):
        config.get_port()
