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
    return PostResult(
        ok=False,
        status_code=405,
        message="Modo solo lectura: crear producto no esta permitido.",
        payload=None,
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
