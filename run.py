import os

import uvicorn

from src.shared.config import load_env
from src.shared.logger import get_logger


def main() -> int:
    logger = get_logger(__name__)
    if not load_env():
        logger.warning(".env no cargado (archivo inexistente o falta python-dotenv)")

    port = int(os.getenv("PORT", "8000"))
    logger.info("Iniciando FastAPI en 0.0.0.0:%d", port)
    uvicorn.run(
        "src.interface_adapter.controllers.api:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
