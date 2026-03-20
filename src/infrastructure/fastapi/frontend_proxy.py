from __future__ import annotations

from typing import Callable
from urllib.parse import urljoin

import httpx
from fastapi import Request, Response

from ...shared.logger import get_logger

logger = get_logger(__name__)

_EXCLUDED_PREFIXES = (
    "/API",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/token",
    "/debug",
    "/observability",
)

_EXCLUDED_EXACT = {"/favicon.ico"}


def is_frontend_route(path: str) -> bool:
    if path in _EXCLUDED_EXACT:
        return False
    return not path.startswith(_EXCLUDED_PREFIXES)


def build_frontend_proxy_middleware(frontend_base_url: str) -> Callable:
    async def frontend_proxy_middleware(request: Request, call_next):
        if request.method not in {"GET", "HEAD"}:
            return await call_next(request)
        if not is_frontend_route(request.url.path):
            return await call_next(request)

        target_url = urljoin(f"{frontend_base_url.rstrip('/')}/", request.url.path.lstrip("/"))
        if request.url.query:
            target_url = f"{target_url}?{request.url.query}"

        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in {"host", "connection", "content-length"}
        }

        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                proxied = client.build_request(
                    request.method,
                    target_url,
                    headers=headers,
                )
                response = await client.send(proxied)
        except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout):
            # Si Vite/dev-server no responde, mantener el comportamiento actual.
            logger.warning(
                "Frontend proxy fallback HTTP hacia estaticos: dev server no disponible (%s)",
                target_url,
            )
            return await call_next(request)
        except httpx.HTTPError as exc:
            logger.warning("Frontend proxy error hacia %s: %s", target_url, exc)
            return await call_next(request)

        proxied_headers = {
            key: value
            for key, value in response.headers.items()
            if key.lower() not in {"transfer-encoding", "connection"}
        }
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=proxied_headers,
            media_type=response.headers.get("content-type"),
        )

    return frontend_proxy_middleware
