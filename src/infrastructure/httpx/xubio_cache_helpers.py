"""
Path: src/infrastructure/httpx/xubio_cache_helpers.py
"""

import os
import time
from copy import deepcopy
from typing import Any, Dict, Hashable, Optional, Tuple

from ...shared.config import is_prod

CacheStore = Dict[Hashable, Tuple[float, Any]]

_TRUE_VALUES = {"1", "true", "yes", "y", "on"}
_FALSE_VALUES = {"0", "false", "no", "n", "off"}


def read_cache_ttl(env_key: str, *, default: float = 60.0) -> float:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value


def read_cache_enabled(env_key: str, *, default: bool) -> bool:
    raw = os.getenv(env_key, "").strip().lower()
    if not raw:
        return default
    if raw in _TRUE_VALUES:
        return True
    if raw in _FALSE_VALUES:
        return False
    return default


def default_get_cache_enabled() -> bool:
    return read_cache_enabled("XUBIO_GET_CACHE_ENABLED", default=not is_prod())


def cache_get(store: CacheStore, key: Hashable, *, ttl: float) -> Optional[Any]:
    if ttl <= 0:
        return None
    entry = store.get(key)
    if entry is None:
        return None
    timestamp, value = entry
    if time.time() - timestamp > ttl:
        store.pop(key, None)
        return None
    return deepcopy(value)


def cache_set(store: CacheStore, key: Hashable, value: Any, *, ttl: float) -> None:
    if ttl <= 0:
        return
    store[key] = (time.time(), deepcopy(value))
