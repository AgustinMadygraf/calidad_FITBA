from typing import Any, Mapping, Optional, Sequence


def match_any_id(item: Mapping[str, Any], target_id: int, keys: Sequence[str]) -> bool:
    for key in keys:
        if item.get(key) == target_id:
            return True
    return False


def extract_int_id(
    item: Mapping[str, Any],
    keys: Sequence[str],
) -> Optional[int]:
    for key in keys:
        value = item.get(key)
        if isinstance(value, int):
            return value
    return None


def first_non_none(*values: Any) -> Optional[Any]:
    for value in values:
        if value is not None:
            return value
    return None
