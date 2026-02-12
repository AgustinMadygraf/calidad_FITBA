import base64
import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


TRUE_VALUES = {"1", "true", "yes", "y", "on"}
FALSE_VALUES = {"0", "false", "no", "n", "off"}

# ---------------------------------------------------------------------------
# TEAM-EDITABLE CONFIGURATION
# Edit only this section to adjust runtime behavior across environments.
# Precedence for IS_PROD:
# 1) set_runtime_is_prod(...) at runtime (e.g. run.py --IS_PROD=...)
# 2) optional IS_PROD from process env (backward compatibility)
# 3) APP_IS_PROD default below
# ---------------------------------------------------------------------------

# App runtime defaults
APP_HOST = "localhost"
APP_PORT = 8000
APP_IS_PROD = False

# Xubio integration defaults
XUBIO_TOKEN_ENDPOINT = "https://xubio.com/API/1.1/TokenEndpoint"
# When None, falls back to `not is_prod()`
XUBIO_GET_CACHE_ENABLED: Optional[bool] = None
XUBIO_LIST_TTL_SECONDS = {
    "XUBIO_CLIENTE_LIST_TTL": 30.0,
    "XUBIO_REMITO_LIST_TTL": 15.0,
    "XUBIO_PRODUCTO_LIST_TTL": 60.0,
    "XUBIO_DEPOSITO_LIST_TTL": 60.0,
    "XUBIO_MONEDA_LIST_TTL": 60.0,
    "XUBIO_LISTA_PRECIO_LIST_TTL": 60.0,
    "XUBIO_CATEGORIA_FISCAL_LIST_TTL": 60.0,
    "XUBIO_IDENTIFICACION_TRIBUTARIA_LIST_TTL": 60.0,
}

# ---------------------------------------------------------------------------
# INTERNALS (avoid edits unless changing config behavior itself)
# ---------------------------------------------------------------------------

_RUNTIME_IS_PROD: Optional[bool] = None


def build_xubio_token() -> str:
    """
    Genera un token base64 a partir de variables de entorno.
    - Usa XUBIO_CLIENT_ID.
    - Usa XUBIO_SECRET_ID.
    """
    client_id = os.getenv("XUBIO_CLIENT_ID", "")
    client_secret = os.getenv("XUBIO_SECRET_ID", "")

    if not client_id or not client_secret:
        raise ValueError("Faltan XUBIO_CLIENT_ID o XUBIO_SECRET_ID")

    raw = f"{client_id}:{client_secret}"
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")


def load_env(env_path: Path | None = None) -> bool:
    if env_path is None:
        env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return False
    if load_dotenv is None:
        return False
    load_dotenv(env_path)
    return True


def is_prod() -> bool:
    if _RUNTIME_IS_PROD is not None:
        return _RUNTIME_IS_PROD
    value = os.getenv("IS_PROD", "")
    parsed = _parse_bool(value)
    if parsed is None:
        return APP_IS_PROD
    return parsed


def set_runtime_is_prod(value: Optional[bool | str]) -> None:
    global _RUNTIME_IS_PROD  # pylint: disable=global-statement
    if value is None:
        _RUNTIME_IS_PROD = None
        return
    if isinstance(value, bool):
        _RUNTIME_IS_PROD = value
        return
    parsed = _parse_bool(value)
    if parsed is None:
        raise ValueError("IS_PROD debe ser booleano o string valido")
    _RUNTIME_IS_PROD = parsed


def get_host() -> str:
    return APP_HOST


def get_port() -> int:
    return APP_PORT


def get_xubio_token_endpoint() -> str:
    return XUBIO_TOKEN_ENDPOINT


def get_cache_ttl(config_key: str, *, default: float = 60.0) -> float:
    value = XUBIO_LIST_TTL_SECONDS.get(config_key, default)
    return float(value)


def get_cache_enabled(config_key: str, *, default: bool) -> bool:
    if config_key != "XUBIO_GET_CACHE_ENABLED":
        return default
    if XUBIO_GET_CACHE_ENABLED is None:
        return default
    return bool(XUBIO_GET_CACHE_ENABLED)


def _parse_bool(raw: str) -> Optional[bool]:
    value = raw.strip().lower()
    if not value:
        return None
    if value in TRUE_VALUES:
        return True
    if value in FALSE_VALUES:
        return False
    return None
