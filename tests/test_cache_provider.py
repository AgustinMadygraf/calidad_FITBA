import pytest

from src.infrastructure.httpx import cache_provider


def test_inmemory_provider_set_get_delete_and_clear():
    provider = cache_provider.InMemoryCacheProvider()

    provider.set("k1", {"x": 1}, ttl=60)
    assert provider.get("k1", ttl=60) == {"x": 1}

    provider.delete("k1")
    assert provider.get("k1", ttl=60) is None

    provider.set("k2", {"y": 2}, ttl=60)
    provider.set("k3", {"z": 3}, ttl=60)
    provider.clear()
    assert provider.store == {}


def test_inmemory_provider_expires_entries():
    provider = cache_provider.InMemoryCacheProvider()
    provider.set("k1", {"x": 1}, ttl=60)

    timestamp, value = provider.store["k1"]
    provider.store["k1"] = (timestamp - 120.0, value)

    assert provider.get("k1", ttl=1) is None
    assert "k1" not in provider.store


def test_build_cache_provider_defaults_to_memory(monkeypatch):
    monkeypatch.delenv(cache_provider.CACHE_PROVIDER_ENV, raising=False)
    provider = cache_provider.build_cache_provider(namespace="test")
    assert isinstance(provider, cache_provider.InMemoryCacheProvider)


def test_build_cache_provider_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv(cache_provider.CACHE_PROVIDER_ENV, "bad-provider")
    with pytest.raises(ValueError):
        cache_provider.build_cache_provider(namespace="test")


def test_build_cache_provider_redis_requires_dependency(monkeypatch):
    monkeypatch.setenv(cache_provider.CACHE_PROVIDER_ENV, "redis")
    monkeypatch.setattr(
        cache_provider,
        "import_module",
        lambda _name: (_ for _ in ()).throw(ModuleNotFoundError("redis")),
    )

    with pytest.raises(RuntimeError):
        cache_provider.build_cache_provider(namespace="test")


def test_providers_for_module_returns_list_and_item_providers(monkeypatch):
    monkeypatch.setenv(cache_provider.CACHE_PROVIDER_ENV, "memory")
    list_provider, item_provider = cache_provider.providers_for_module(
        namespace="producto",
        with_item_cache=True,
    )
    assert isinstance(list_provider, cache_provider.InMemoryCacheProvider)
    assert isinstance(item_provider, cache_provider.InMemoryCacheProvider)
