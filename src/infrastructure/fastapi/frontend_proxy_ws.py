from __future__ import annotations

import contextlib
from urllib.parse import urlparse

import anyio
from fastapi import WebSocket, WebSocketDisconnect

from ...shared.logger import get_logger
from .frontend_proxy import is_frontend_route

logger = get_logger(__name__)

try:
    import websockets
    from websockets.exceptions import WebSocketException
except ImportError:  # pragma: no cover - env-dependent branch
    websockets = None
    WebSocketException = Exception


def _to_ws_url(frontend_base_url: str, path: str, query_string: str) -> str:
    parsed = urlparse(frontend_base_url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    netloc = parsed.netloc or parsed.path
    base_path = (parsed.path or "").rstrip("/")
    full_path = f"{base_path}/{path}".replace("//", "/")
    if not full_path.startswith("/"):
        full_path = f"/{full_path}"
    ws_url = f"{scheme}://{netloc}{full_path}"
    if query_string:
        ws_url = f"{ws_url}?{query_string}"
    return ws_url


def build_frontend_ws_proxy_handler(frontend_base_url: str):
    async def frontend_ws_proxy(websocket: WebSocket, full_path: str) -> None:
        if websockets is None:
            logger.warning("Proxy WS frontend deshabilitado: falta dependencia websockets")
            await websocket.close(code=1011, reason="WS proxy dependency missing")
            return

        path = f"/{full_path.lstrip('/')}" if full_path else "/"
        if not is_frontend_route(path):
            await websocket.close(code=1008, reason="Not a frontend websocket route")
            return

        query_string = websocket.scope.get("query_string", b"").decode("utf-8")
        target_ws_url = _to_ws_url(frontend_base_url, full_path, query_string)

        incoming_headers = dict(websocket.headers.items())
        extra_headers = {
            key: value
            for key, value in incoming_headers.items()
            if key.lower()
            not in {
                "host",
                "connection",
                "upgrade",
                "sec-websocket-key",
                "sec-websocket-version",
                "sec-websocket-extensions",
                "sec-websocket-protocol",
            }
        }

        subprotocols = list(websocket.scope.get("subprotocols", []))

        try:
            connect_kwargs = {
                "subprotocols": subprotocols,
                "ping_interval": 20,
                "ping_timeout": 20,
                "close_timeout": 5,
            }
            if extra_headers:
                connect_kwargs["additional_headers"] = extra_headers
            try:
                upstream_ctx = websockets.connect(target_ws_url, **connect_kwargs)
            except TypeError:
                if "additional_headers" in connect_kwargs:
                    connect_kwargs["extra_headers"] = connect_kwargs.pop(
                        "additional_headers"
                    )
                upstream_ctx = websockets.connect(target_ws_url, **connect_kwargs)

            async with upstream_ctx as upstream:
                await websocket.accept(subprotocol=upstream.subprotocol)

                async def client_to_upstream() -> None:
                    while True:
                        message = await websocket.receive()
                        msg_type = message["type"]
                        if msg_type == "websocket.disconnect":
                            with contextlib.suppress(Exception):
                                await upstream.close(code=1000)
                            return
                        if message.get("text") is not None:
                            text = message["text"]
                            await upstream.send(text)
                            continue
                        if message.get("bytes") is not None:
                            data = message["bytes"]
                            await upstream.send(data)

                async def upstream_to_client() -> None:
                    try:
                        async for message in upstream:
                            if isinstance(message, bytes):
                                await websocket.send_bytes(message)
                            else:
                                await websocket.send_text(message)
                    finally:
                        with contextlib.suppress(Exception):
                            await websocket.close(code=1000)

                async with anyio.create_task_group() as tg:
                    tg.start_soon(client_to_upstream)
                    tg.start_soon(upstream_to_client)

        except (OSError, WebSocketException) as exc:
            logger.warning("WS frontend proxy fallback (%s): %s", target_ws_url, exc)
            with contextlib.suppress(Exception):
                await websocket.close(code=1013, reason="Frontend dev server unavailable")
        except WebSocketDisconnect:
            with contextlib.suppress(Exception):
                await websocket.close(code=1000)

    return frontend_ws_proxy
