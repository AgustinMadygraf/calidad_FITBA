import os
import sys

import uvicorn

from src.shared.config import load_env
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
            os.environ["IS_PROD"] = value
        elif arg == "--IS_PROD" and idx + 1 < len(argv):
            os.environ["IS_PROD"] = argv[idx + 1]

    host = os.getenv("HOST", "localhost")
    port = int(os.getenv("PORT", "8000"))
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
