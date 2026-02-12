import time

from src.infrastructure.httpx import xubio_cache_helpers as cache_helpers


def test_default_get_cache_enabled_uses_runtime_default(monkeypatch):
    monkeypatch.setattr(cache_helpers, "is_prod", lambda: False)
    monkeypatch.setattr(
        cache_helpers,
        "read_cache_enabled",
        lambda key, default: default if key == "XUBIO_GET_CACHE_ENABLED" else False,
    )
    assert cache_helpers.default_get_cache_enabled() is True

    monkeypatch.setattr(cache_helpers, "is_prod", lambda: True)
    monkeypatch.setattr(
        cache_helpers,
        "read_cache_enabled",
        lambda key, default: default if key == "XUBIO_GET_CACHE_ENABLED" else True,
    )
    assert cache_helpers.default_get_cache_enabled() is False


def test_cache_get_and_set_behaviour(monkeypatch):
    store = {}
    cache_helpers.cache_set(store, "k", {"value": 1}, ttl=60)
    assert cache_helpers.cache_get(store, "k", ttl=60) == {"value": 1}

    # Ensure deep copy semantics.
    fetched = cache_helpers.cache_get(store, "k", ttl=60)
    fetched["value"] = 99
    assert cache_helpers.cache_get(store, "k", ttl=60) == {"value": 1}

    # ttl <= 0 bypasses cache.
    assert cache_helpers.cache_get(store, "k", ttl=0) is None
    cache_helpers.cache_set(store, "x", {"v": 1}, ttl=0)
    assert "x" not in store

    # Expired entries are removed.
    now = time.time()
    monkeypatch.setattr(cache_helpers.time, "time", lambda: now + 120)
    assert cache_helpers.cache_get(store, "k", ttl=1) is None
    assert "k" not in store

