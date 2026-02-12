import sys

import uvicorn

from src.shared.config import get_host, get_port, load_env, set_runtime_is_prod
from src.shared.logger import get_logger


def main() -> int:
    logger = get_logger(__name__)
    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    # Allow CLI override: --IS_PROD=true|false
    argv = sys.argv[1:]
    for idx, arg in enumerate(argv):
        if arg.startswith("--IS_PROD="):
            _, value = arg.split("=", 1)
            set_runtime_is_prod(value)
        elif arg == "--IS_PROD" and idx + 1 < len(argv):
            set_runtime_is_prod(argv[idx + 1])

    host = get_host()
    port = get_port()
    logger.info("Iniciando FastAPI en %s:%d", host, port)
    uvicorn.run(
        "src.infrastructure.fastapi.api:app",
        host=host,
        port=port,
        reload=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
