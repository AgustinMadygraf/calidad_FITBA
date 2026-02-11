"""
Path: src/infrastructure/httpx/xubio_cache_helpers.py
"""

import os


def read_cache_ttl(env_key: str, *, default: float = 60.0) -> float:
    raw = os.getenv(env_key, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value
