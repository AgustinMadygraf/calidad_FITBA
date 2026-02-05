from dotenv import load_dotenv
from pathlib import Path
import sys
from cliente.infrastructure.api_client import ApiClient
from cliente.presentation.cli.menu import main_menu


def _resolve_env_path() -> Path | None:
    if getattr(sys, "_MEIPASS", None):
        bundled = Path(sys._MEIPASS) / ".env"
        if bundled.exists():
            return bundled
    cwd_env = Path(".env")
    if cwd_env.exists():
        return cwd_env
    return None


def run() -> None:
    env_path = _resolve_env_path()
    if env_path is not None:
        load_dotenv(env_path)
    else:
        load_dotenv()
    api = ApiClient()
    try:
        main_menu(api)
    except Exception as exc:
        print(f"Error inesperado: {exc}")
    finally:
        api.close()
