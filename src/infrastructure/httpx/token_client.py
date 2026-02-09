"""
Path: src/infrastructure/httpx/token_client.py
"""

import os
import time
from typing import Any, Dict, Optional

import httpx

from ...shared.config import build_xubio_token

_CACHE: Dict[str, Any] = {
    "access_token": None,
    "token_type": None,
    "scope": None,
    "expires_at": 0,
}


def build_token_request() -> Dict[str, str]:
    """
    Retorna los parametros minimos para pedir un token OAuth2.
    """
    return {
        "grant_type": "client_credentials",
    }


def build_auth_header() -> str:
    return f"Basic {build_xubio_token()}"


def get_token_endpoint() -> str:
    return os.getenv("XUBIO_TOKEN_ENDPOINT", "https://xubio.com/API/1.1/TokenEndpoint")


def _now() -> int:
    return int(time.time())


def _cache_valid(leeway_seconds: int = 10) -> bool:
    token = _CACHE.get("access_token")
    expires_at = int(_CACHE.get("expires_at") or 0)
    return bool(token) and (_now() + leeway_seconds) < expires_at


def _preview_token(token: str, head: int = 6, tail: int = 4) -> str:
    if len(token) <= head + tail:
        return token
    return f"{token[:head]}...{token[-tail:]}"


def fetch_access_token(timeout: Optional[float] = 10.0, *, force_refresh: bool = False) -> Dict[str, Any]:
    if not force_refresh and _cache_valid():
        remaining = max(0, int(_CACHE["expires_at"] - _now()))
        return {
            "access_token": _CACHE["access_token"],
            "token_type": _CACHE["token_type"],
            "scope": _CACHE["scope"],
            "expires_in": remaining,
            "expires_at": _CACHE["expires_at"],
            "from_cache": True,
        }

    token_endpoint = get_token_endpoint()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": build_auth_header(),
    }
    data = build_token_request()

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(token_endpoint, data=data, headers=headers)

    if resp.status_code >= 400:
        raise RuntimeError(f"TokenEndpoint error {resp.status_code}: {resp.text}")

    payload = resp.json()
    access_token = payload.get("access_token")
    expires_in_raw = payload.get("expires_in")
    token_type = payload.get("token_type")
    scope = payload.get("scope")

    if not access_token:
        raise RuntimeError("TokenEndpoint response sin access_token")
    try:
        expires_in = int(expires_in_raw)
    except (TypeError, ValueError):
        raise RuntimeError("TokenEndpoint response sin expires_in valido")

    _CACHE["access_token"] = access_token
    _CACHE["token_type"] = token_type
    _CACHE["scope"] = scope
    _CACHE["expires_at"] = _now() + expires_in

    return {
        "access_token": access_token,
        "token_type": token_type,
        "scope": scope,
        "expires_in": expires_in,
        "expires_at": _CACHE["expires_at"],
        "from_cache": False,
    }


def is_invalid_token_response(resp: httpx.Response) -> bool:
    try:
        payload = resp.json()
    except ValueError:
        return False
    if isinstance(payload, dict):
        return payload.get("error") == "invalid_token"
    return False


def get_token_status(timeout: Optional[float] = 10.0) -> Dict[str, Any]:
    info = fetch_access_token(timeout=timeout, force_refresh=False)
    remaining = max(0, int(info["expires_at"] - _now()))
    return {
        "token_preview": _preview_token(info["access_token"]),
        "expires_in_seconds": remaining,
        "expires_at": info["expires_at"],
        "from_cache": info.get("from_cache", False),
    }


def request_with_token(
    method: str,
    url: str,
    *,
    timeout: Optional[float] = 10.0,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    data: Optional[Dict[str, str]] = None,
    json: Optional[Dict[str, str]] = None,
) -> httpx.Response:
    """
    Request con refresh simple si el token es invalido.
    """
    token_info = fetch_access_token(timeout=timeout)
    token = token_info["access_token"]
    base_headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    if headers:
        base_headers.update(headers)

    with httpx.Client(timeout=timeout) as client:
        resp = client.request(
            method, url, headers=base_headers, params=params, data=data, json=json
        )

        if is_invalid_token_response(resp):
            token_info = fetch_access_token(timeout=timeout, force_refresh=True)
            token = token_info["access_token"]
            base_headers["Authorization"] = f"Bearer {token}"
            resp = client.request(
                method, url, headers=base_headers, params=params, data=data, json=json
            )

    return resp
