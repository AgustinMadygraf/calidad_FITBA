import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.catalogos import deposito_list
from src.infrastructure.memory.deposito_gateway_memory import InMemoryDepositoGateway


def test_get_depositos_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.deposito_gateway = InMemoryDepositoGateway()
    data = deposito_list()
    assert "items" in data
    assert isinstance(data["items"], list)
