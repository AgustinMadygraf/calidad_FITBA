from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import httpx

from ...use_cases.ports.terminal_cli_product_gateway import TerminalCliProductGateway
from ...use_cases.terminal_cli import PostResult
from .token_client import request_with_token

PRODUCT_CREATE_PATH = "/API/1.1/ProductoVentaBean"


def build_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}{path}"


def safe_json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def extract_error_detail(raw_payload: Any, response: httpx.Response) -> str:
    if isinstance(raw_payload, dict):
        detail = raw_payload.get("detail")
        if detail is not None:
            return str(detail)
    text = getattr(response, "text", "")
    return text.strip()[:300]


def post_product(
    base_url: str,
    payload: Dict[str, Any],
    timeout: float,
    request_executor: Optional[Callable[..., httpx.Response]] = None,
) -> PostResult:
    url = build_url(base_url, PRODUCT_CREATE_PATH)
    request_fn = request_executor or request_with_token
    try:
        response = request_fn("POST", url, json=payload, timeout=timeout)
    except httpx.HTTPError as exc:
        return PostResult(
            ok=False,
            status_code=None,
            message=f"Error HTTP al crear producto: {exc}",
            payload=None,
        )
    except RuntimeError as exc:
        return PostResult(
            ok=False,
            status_code=None,
            message=f"Error OAuth2 al crear producto: {exc}",
            payload=None,
        )

    raw_payload = safe_json(response)
    payload_dict = raw_payload if isinstance(raw_payload, dict) else None

    if 200 <= response.status_code < 300:
        return PostResult(
            ok=True,
            status_code=response.status_code,
            message=f"Producto creado correctamente (HTTP {response.status_code}).",
            payload=payload_dict,
        )

    detail = extract_error_detail(raw_payload, response)
    if response.status_code == 403:
        message = (
            "Operacion rechazada (HTTP 403): revisa permisos/token OAuth2 o "
            "politicas del servidor destino."
        )
    elif response.status_code == 401:
        message = (
            "No autorizado (HTTP 401): revisa credenciales OAuth2 "
            "(client-id/secret-id/access_token)."
        )
    elif detail:
        message = f"Error al crear producto (HTTP {response.status_code}): {detail}"
    else:
        message = f"Error al crear producto (HTTP {response.status_code})."

    return PostResult(
        ok=False,
        status_code=response.status_code,
        message=message,
        payload=payload_dict,
    )


class XubioTerminalCliProductGateway(TerminalCliProductGateway):
    def __init__(
        self,
        request_executor: Optional[Callable[..., httpx.Response]] = None,
    ) -> None:
        self._request_executor = request_executor

    def create_product(
        self,
        base_url: str,
        payload: Dict[str, Any],
        timeout: float,
    ) -> PostResult:
        return post_product(
            base_url=base_url,
            payload=payload,
            timeout=timeout,
            request_executor=self._request_executor,
        )
