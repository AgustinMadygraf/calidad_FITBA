from typing import Any, Dict


def present(status: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "status": "ok",
        "token_preview": status.get("token_preview"),
        "expires_in_seconds": status.get("expires_in_seconds"),
        "expires_at": status.get("expires_at"),
        "from_cache": status.get("from_cache"),
    }
