import os
import socket

import uvicorn

from src.shared.config import get_host, get_port, load_env
from src.shared.logger import get_logger


def _ensure_port_available(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError as exc:
            if exc.errno == 98:
                raise RuntimeError(
                    "Puerto ocupado. Libera el puerto o cambia APP_PORT. "
                    f"Sugerencia: lsof -i :{port}"
                ) from exc
            raise


def _resolve_bind_port(host: str, preferred_port: int, *, max_tries: int = 20) -> int:
    for offset in range(max_tries + 1):
        candidate = preferred_port + offset
        try:
            _ensure_port_available(host, candidate)
            return candidate
        except RuntimeError:
            continue
    raise RuntimeError(
        f"No se encontro puerto disponible entre {preferred_port} y {preferred_port + max_tries}. "
        f"Sugerencia: lsof -i :{preferred_port}"
    )


def main() -> int:
    logger = get_logger(__name__)
    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    try:
        host = get_host()
        port = get_port()
    except ValueError as exc:
        logger.error("Configuracion invalida: %s", exc)
        return 2

    try:
        resolved_port = _resolve_bind_port(host, port)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1
    if resolved_port != port:
        logger.warning(
            "Puerto %d ocupado. Se usara automaticamente el puerto %d.",
            port,
            resolved_port,
        )
    port = resolved_port

    reload_enabled = os.getenv("FASTAPI_RELOAD", "true").lower() == "true"
    logger.info("Iniciando FastAPI en %s:%d", host, port)
    uvicorn.run(
        "src.infrastructure.fastapi.api:app",
        host=host,
        port=port,
        reload=reload_enabled,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
