import os

from src.infrastructure.fastapi.api import deposito_list
from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway


def test_get_depositos_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.deposito_gateway = InMemoryDepositoGateway()
    data = deposito_list()
    assert "items" in data
    assert isinstance(data["items"], list)
