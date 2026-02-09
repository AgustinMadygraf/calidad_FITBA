from typing import Any, Dict

from ..infrastructure.httpx.token_client import get_token_status


def execute() -> Dict[str, Any]:
    return get_token_status()
