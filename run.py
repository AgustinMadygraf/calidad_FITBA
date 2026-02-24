import os

import uvicorn

from src.shared.config import get_host, get_port, load_env
from src.shared.logger import get_logger


def main() -> int:
    logger = get_logger(__name__)
    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    host = get_host()
    port = get_port()
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
