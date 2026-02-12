from pathlib import Path

import pytest

import src.shared.config as config


@pytest.fixture(autouse=True)
def reset_runtime_is_prod():
    config.set_runtime_is_prod(None)
    yield
    config.set_runtime_is_prod(None)


def test_build_xubio_token_success(monkeypatch):
    monkeypatch.setenv("XUBIO_CLIENT_ID", "cid")
    monkeypatch.setenv("XUBIO_SECRET_ID", "sid")

    token = config.build_xubio_token()

    assert token == "Y2lkOnNpZA=="


def test_build_xubio_token_missing_env(monkeypatch):
    monkeypatch.delenv("XUBIO_CLIENT_ID", raising=False)
    monkeypatch.delenv("XUBIO_SECRET_ID", raising=False)

    with pytest.raises(ValueError, match="Faltan XUBIO_CLIENT_ID o XUBIO_SECRET_ID"):
        config.build_xubio_token()


def test_load_env_variants(monkeypatch, tmp_path):
    missing = tmp_path / "missing.env"
    assert config.load_env(missing) is False

    existing = tmp_path / ".env"
    existing.write_text("KEY=VAL\n", encoding="utf-8")

    monkeypatch.setattr(config, "load_dotenv", None)
    assert config.load_env(existing) is False

    called = {}

    def fake_load_dotenv(path):
        called["path"] = path
        return True

    monkeypatch.setattr(config, "load_dotenv", fake_load_dotenv)
    assert config.load_env(existing) is True
    assert called["path"] == existing


def test_is_prod_precedence(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    assert config.is_prod() is True

    config.set_runtime_is_prod(False)
    assert config.is_prod() is False

    config.set_runtime_is_prod(None)
    monkeypatch.setenv("IS_PROD", "no")
    assert config.is_prod() is False


def test_set_runtime_is_prod_validation():
    config.set_runtime_is_prod(True)
    assert config.is_prod() is True

    config.set_runtime_is_prod("false")
    assert config.is_prod() is False

    with pytest.raises(ValueError, match="IS_PROD debe ser booleano o string valido"):
        config.set_runtime_is_prod("maybe")


def test_getters_and_cache_helpers(monkeypatch):
    assert config.get_host() == config.APP_HOST
    assert config.get_port() == config.APP_PORT
    assert config.get_xubio_token_endpoint() == config.XUBIO_TOKEN_ENDPOINT

    monkeypatch.setitem(config.XUBIO_LIST_TTL_SECONDS, "XUBIO_CUSTOM_TTL", 12.5)
    assert config.get_cache_ttl("XUBIO_CUSTOM_TTL") == 12.5
    assert config.get_cache_ttl("UNKNOWN", default=7.0) == 7.0

    monkeypatch.setattr(config, "XUBIO_GET_CACHE_ENABLED", None)
    assert config.get_cache_enabled("XUBIO_GET_CACHE_ENABLED", default=True) is True
    monkeypatch.setattr(config, "XUBIO_GET_CACHE_ENABLED", False)
    assert config.get_cache_enabled("XUBIO_GET_CACHE_ENABLED", default=True) is False
    assert config.get_cache_enabled("OTHER_KEY", default=False) is False


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("", None),
        ("true", True),
        ("YES", True),
        ("0", False),
        ("off", False),
        ("invalid", None),
    ],
)
def test_parse_bool(raw, expected):
    assert config._parse_bool(raw) is expected

