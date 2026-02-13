from __future__ import annotations

import json
import os
from copy import deepcopy
from importlib import import_module
from time import time
from typing import Any, Hashable, Optional, Protocol, Tuple

from .xubio_cache_helpers import CacheStore

DEFAULT_CACHE_PROVIDER = "memory"
CACHE_PROVIDER_ENV = "XUBIO_CACHE_PROVIDER"
REDIS_URL_ENV = "XUBIO_REDIS_URL"
REDIS_PREFIX_ENV = "XUBIO_REDIS_PREFIX"
DEFAULT_REDIS_URL = "redis://127.0.0.1:6379/0"
DEFAULT_REDIS_PREFIX = "xubio-cache"


class CacheProvider(Protocol):
    @property
    def store(self) -> CacheStore:
        pass

    def get(self, key: Hashable, *, ttl: float) -> Optional[Any]:
        pass

    def set(self, key: Hashable, value: Any, *, ttl: float) -> None:
        pass

    def delete(self, key: Hashable) -> None:
        pass

    def clear(self) -> None:
        pass


class InMemoryCacheProvider:
    def __init__(self, store: Optional[CacheStore] = None) -> None:
        self._store: CacheStore = store if store is not None else {}

    @property
    def store(self) -> CacheStore:
        return self._store

    def get(self, key: Hashable, *, ttl: float) -> Optional[Any]:
        if ttl <= 0:
            return None
        entry = self._store.get(key)
        if entry is None:
            return None
        timestamp, value = entry

        if time() - timestamp > ttl:
            self._store.pop(key, None)
            return None
        return deepcopy(value)

    def set(self, key: Hashable, value: Any, *, ttl: float) -> None:
        if ttl <= 0:
            return

        self._store[key] = (time(), deepcopy(value))

    def delete(self, key: Hashable) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


class RedisCacheProvider:
    def __init__(self, client: Any, *, prefix: str) -> None:
        self._client = client
        self._prefix = prefix.rstrip(":")
        self._debug_store: CacheStore = {}

    @property
    def store(self) -> CacheStore:
        # Kept for backward-compatible test hooks; Redis state lives remotely.
        return self._debug_store

    def _redis_key(self, key: Hashable) -> str:
        return f"{self._prefix}:{key}"

    def get(self, key: Hashable, *, ttl: float) -> Optional[Any]:
        if ttl <= 0:
            return None
        redis_key = self._redis_key(key)
        raw = self._client.get(redis_key)
        if raw is None:
            return None
        try:
            payload = json.loads(raw)
            timestamp = float(payload["timestamp"])
            value = payload["value"]
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self._client.delete(redis_key)
            return None
        if time() - timestamp > ttl:
            self._client.delete(redis_key)
            return None
        return deepcopy(value)

    def set(self, key: Hashable, value: Any, *, ttl: float) -> None:
        if ttl <= 0:
            return
        redis_key = self._redis_key(key)
        payload = json.dumps({"timestamp": time(), "value": value}, ensure_ascii=False)
        self._client.set(redis_key, payload)

    def delete(self, key: Hashable) -> None:
        self._client.delete(self._redis_key(key))

    def clear(self) -> None:
        pattern = f"{self._prefix}:*"
        keys = list(self._client.scan_iter(match=pattern))
        if keys:
            self._client.delete(*keys)


def build_cache_provider(*, namespace: str) -> CacheProvider:
    provider_kind = os.getenv(CACHE_PROVIDER_ENV, DEFAULT_CACHE_PROVIDER).strip().lower()
    if provider_kind in {"memory", "in-memory", "inmemory"}:
        return InMemoryCacheProvider()
    if provider_kind != "redis":
        raise ValueError(
            f"{CACHE_PROVIDER_ENV} invalido: '{provider_kind}'. Usar memory o redis."
        )
    return _build_redis_provider(namespace=namespace)


def _build_redis_provider(*, namespace: str) -> CacheProvider:
    try:
        redis_module = import_module("redis")
    except Exception as exc:
        raise RuntimeError(
            "Cache provider 'redis' requiere paquete 'redis'. "
            "Instalar con: pip install redis"
        ) from exc
    redis_url = os.getenv(REDIS_URL_ENV, DEFAULT_REDIS_URL).strip()
    redis_prefix = os.getenv(REDIS_PREFIX_ENV, DEFAULT_REDIS_PREFIX).strip() or DEFAULT_REDIS_PREFIX
    client = redis_module.Redis.from_url(redis_url, decode_responses=True)
    return RedisCacheProvider(client, prefix=f"{redis_prefix}:{namespace}")


def providers_for_module(
    *,
    namespace: str,
    with_item_cache: bool = False,
) -> Tuple[CacheProvider, Optional[CacheProvider]]:
    list_provider = build_cache_provider(namespace=f"{namespace}:list")
    if not with_item_cache:
        return list_provider, None
    item_provider = build_cache_provider(namespace=f"{namespace}:item")
    return list_provider, item_provider
