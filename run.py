import argparse

import uvicorn

from src.infrastructure.runtime import server_startup
from src.shared.config import load_env
from src.shared.logger import get_logger

# Backward-compat aliases used by tests.
_ensure_port_available = server_startup.ensure_port_available
_resolve_bind_port = server_startup.resolve_bind_port


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run FastAPI backend.")
    parser.add_argument(
        "--mode",
        choices=["ngrok", "red-interna", "full"],
        default="ngrok",
        help=(
            "Modo de exposición del backend: "
            "ngrok (127.0.0.1), red-interna (0.0.0.0), full (0.0.0.0)."
        ),
    )
    return parser


def main() -> int:
    logger = get_logger(__name__)
    args = _build_parser().parse_args()

    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    try:
        runtime = server_startup.bootstrap_runtime(args.mode, logger)
    except ValueError as exc:
        logger.error("Configuracion invalida: %s", exc)
        return 2
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1

    uvicorn.run(
        "src.infrastructure.fastapi.api:app",
        host=runtime.host,
        port=runtime.port,
        reload=runtime.reload_enabled,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
