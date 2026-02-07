from __future__ import annotations

from typing import Any


def parse_bool(value: Any, field_name: str = "IS_PROD") -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "false", "1", "0", "yes", "no"}:
            return normalized in {"true", "1", "yes"}
    raise ValueError(f"{field_name} debe ser booleano (true/false).")
