"""
Path: src/infrastructure/httpx/token_client.py
"""

import time
from typing import Any, Dict, Optional

import httpx

from ...shared.config import build_xubio_token, get_xubio_token_endpoint
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
    return get_xubio_token_endpoint()


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


def _cached_token_info() -> Optional[Dict[str, Any]]:
    if not _cache_valid():
        return None
    remaining = max(0, int(_CACHE["expires_at"] - _now()))
    return {
        "access_token": _CACHE["access_token"],
        "token_type": _CACHE["token_type"],
        "scope": _CACHE["scope"],
        "expires_in": remaining,
        "expires_at": _CACHE["expires_at"],
        "from_cache": True,
    }


def _request_token(timeout: Optional[float]) -> httpx.Response:
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

    return resp


def _parse_token_payload(payload: Any) -> tuple[str, int, Optional[str], Optional[str]]:
    if not isinstance(payload, dict):
        raise RuntimeError("TokenEndpoint response sin JSON valido")
    access_token = payload.get("access_token")
    if not access_token:
        raise RuntimeError("TokenEndpoint response sin access_token")
    expires_in_raw = payload.get("expires_in")
    try:
        expires_in = int(expires_in_raw)
    except (TypeError, ValueError) as exc:
        raise RuntimeError("TokenEndpoint response sin expires_in valido") from exc
    return access_token, expires_in, payload.get("token_type"), payload.get("scope")


def _store_token(
    access_token: str,
    token_type: Optional[str],
    scope: Optional[str],
    expires_in: int,
) -> int:
    expires_at = _now() + expires_in
    _CACHE["access_token"] = access_token
    _CACHE["token_type"] = token_type
    _CACHE["scope"] = scope
    _CACHE["expires_at"] = expires_at
    return expires_at


def fetch_access_token(
    timeout: Optional[float] = 10.0, *, force_refresh: bool = False
) -> Dict[str, Any]:
    if not force_refresh:
        cached = _cached_token_info()
        if cached is not None:
            return cached

    resp = _request_token(timeout)
    payload = resp.json()
    access_token, expires_in, token_type, scope = _parse_token_payload(payload)
    expires_at = _store_token(access_token, token_type, scope, expires_in)

    return {
        "access_token": access_token,
        "token_type": token_type,
        "scope": scope,
        "expires_in": expires_in,
        "expires_at": expires_at,
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
    **kwargs: Any,
) -> httpx.Response:
    """
    Request con refresh simple si el token es invalido.
    """
    options = _extract_request_options(kwargs)
    _ensure_no_extra_options(kwargs)
    return _request_with_refresh(method, url, timeout, options)


def _ensure_no_extra_options(options: Dict[str, Any]) -> None:
    if options:
        extra = ", ".join(sorted(options.keys()))
        raise ValueError(f"Opciones no soportadas: {extra}")


def _extract_request_options(options: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "headers": options.pop("headers", None),
        "params": options.pop("params", None),
        "data": options.pop("data", None),
        "json": options.pop("json", None),
    }


def _build_auth_headers(
    token: str, extra_headers: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    return headers


def _request_once(
    method: str,
    url: str,
    timeout: Optional[float],
    options: Dict[str, Any],
    *,
    force_refresh: bool,
) -> httpx.Response:
    token_info = fetch_access_token(timeout=timeout, force_refresh=force_refresh)
    headers = _build_auth_headers(token_info["access_token"], options.get("headers"))
    with httpx.Client(timeout=timeout) as client:
        return client.request(
            method,
            url,
            headers=headers,
            params=options.get("params"),
            data=options.get("data"),
            json=options.get("json"),
        )


def _request_with_refresh(
    method: str, url: str, timeout: Optional[float], options: Dict[str, Any]
) -> httpx.Response:
    resp = _request_once(method, url, timeout, options, force_refresh=False)
    if is_invalid_token_response(resp):
        resp = _request_once(method, url, timeout, options, force_refresh=True)
    return resp
