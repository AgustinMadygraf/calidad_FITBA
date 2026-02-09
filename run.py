import os
from pathlib import Path

import uvicorn

from src.shared.logger import get_logger


def main() -> int:
    logger = get_logger(__name__)
    env_path = Path(__file__).with_name(".env")
    if env_path.exists():
        try:
            from dotenv import load_dotenv
        except ImportError:
            logger.warning("python-dotenv no instalado; no se cargo .env")
        else:
            load_dotenv(env_path)

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
