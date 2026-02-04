from dotenv import load_dotenv
from cliente.infrastructure.api_client import ApiClient
from cliente.presentation.cli.menu import main_menu


def run() -> None:
    load_dotenv()
    api = ApiClient()
    try:
        main_menu(api)
    finally:
        api.close()
