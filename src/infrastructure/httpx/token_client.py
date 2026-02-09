import os
from typing import Dict, Optional

import httpx

from ...shared.config import build_xubio_token


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


def fetch_access_token(timeout: Optional[float] = 10.0) -> str:
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
    if not access_token:
        raise RuntimeError("TokenEndpoint response sin access_token")

    return access_token


def is_invalid_token_response(resp: httpx.Response) -> bool:
    try:
        payload = resp.json()
    except ValueError:
        return False
    return payload.get("error") == "invalid_token"


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
    token = fetch_access_token(timeout=timeout)
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
            token = fetch_access_token(timeout=timeout)
            base_headers["Authorization"] = f"Bearer {token}"
            resp = client.request(
                method, url, headers=base_headers, params=params, data=data, json=json
            )

    return resp
