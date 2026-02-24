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
# ---------------------------------------------------------------------------

# App runtime defaults
APP_HOST = "127.0.0.1"
APP_PORT = 8000
APP_STATIC_DIR = r"/var/www/html/xubio-www"
APP_FRONTEND_DEV_PROXY_URL = "http://127.0.0.1:5173"
APP_FRONTEND_DEV_PROXY_ENABLED = True
APP_FRONTEND_DEV_PROXY_WS_ENABLED = True
APP_NETWORK_AUDIT_DB = ".runtime/network_audit.sqlite3"

# Xubio integration defaults
XUBIO_TOKEN_ENDPOINT = "https://xubio.com/API/1.1/TokenEndpoint"
# When None, falls back to `default`.
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
    "XUBIO_VENDEDOR_LIST_TTL": 60.0,
    "XUBIO_COMPROBANTE_VENTA_LIST_TTL": 60.0,
}

# CORS defaults for browser frontends in local/prod environments.
FRONTEND_CORS_ORIGINS_DEFAULT = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "https://xubio.madygraf.com",
]

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


def get_host() -> str:
    env_value = os.getenv("APP_HOST", "").strip()
    if env_value:
        return env_value
    return APP_HOST


def get_port() -> int:
    raw_value = os.getenv("APP_PORT", "").strip()
    if not raw_value:
        return APP_PORT
    try:
        port = int(raw_value)
    except ValueError as exc:
        raise ValueError("APP_PORT debe ser un entero valido") from exc
    if not (1 <= port <= 65535):
        raise ValueError("APP_PORT debe estar entre 1 y 65535")
    return port


def get_static_dir() -> Path:
    env_value = os.getenv("STATIC_DIR", "").strip()
    if env_value:
        return _resolve_path(env_value)
    return _resolve_path(APP_STATIC_DIR)


def get_frontend_dev_proxy_url() -> str:
    return os.getenv("FRONTEND_DEV_PROXY_URL", APP_FRONTEND_DEV_PROXY_URL).strip()


def is_frontend_dev_proxy_enabled() -> bool:
    raw = os.getenv("FRONTEND_DEV_PROXY_ENABLED", "").strip()
    parsed = _parse_bool(raw)
    if parsed is None:
        return APP_FRONTEND_DEV_PROXY_ENABLED
    return parsed


def is_frontend_dev_proxy_ws_enabled() -> bool:
    raw = os.getenv("FRONTEND_DEV_PROXY_WS_ENABLED", "").strip()
    parsed = _parse_bool(raw)
    if parsed is None:
        return APP_FRONTEND_DEV_PROXY_WS_ENABLED and APP_FRONTEND_DEV_PROXY_ENABLED
    return parsed


def get_xubio_token_endpoint() -> str:
    return XUBIO_TOKEN_ENDPOINT


def get_frontend_cors_origins() -> list[str]:
    raw = os.getenv("FRONTEND_CORS_ORIGINS", "").strip()
    if not raw:
        return FRONTEND_CORS_ORIGINS_DEFAULT.copy()
    origins = [item.strip() for item in raw.split(",") if item.strip()]
    if not origins:
        return FRONTEND_CORS_ORIGINS_DEFAULT.copy()
    return origins


def get_network_audit_db_path() -> str:
    return os.getenv("NETWORK_AUDIT_DB", APP_NETWORK_AUDIT_DB).strip() or APP_NETWORK_AUDIT_DB


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


def _resolve_path(raw: str) -> Path:
    path = Path(raw)
    if path.is_absolute():
        return path
    project_root = Path(__file__).resolve().parents[2]
    return (project_root / path).resolve()
