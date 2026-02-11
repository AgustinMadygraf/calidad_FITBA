"""
Path: src/infrastructure/httpx/xubio_httpx_helpers.py
"""

from typing import Any, Dict, List

import httpx

from ...use_cases.errors import ExternalServiceError


def raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        raise ExternalServiceError(f"Xubio error {resp.status_code}: {resp.text}")


def extract_list(resp: httpx.Response, *, label: str) -> List[Dict[str, Any]]:
    raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ExternalServiceError(f"Respuesta inesperada al listar {label}")
