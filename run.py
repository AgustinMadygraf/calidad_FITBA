import os
import sys

# Make ./src importable when running from repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from shared.config import build_xubio_token
from shared.logger import get_logger


def main() -> int:
    logger = get_logger(__name__)
    token = build_xubio_token()
    # Avoid logging secrets; only log the token length.
    logger.info("Token generado (len=%d)", len(token))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
