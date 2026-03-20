import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.producto import producto_list
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway


def test_get_productos_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.producto_gateway = InMemoryProductoGateway()
    data = producto_list()
    assert "items" in data
    assert isinstance(data["items"], list)
