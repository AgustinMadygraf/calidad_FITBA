import os

from src.infrastructure.fastapi.api import producto_compra_list
from src.infrastructure.fastapi.api import app as global_app
from src.infrastructure.memory.producto_gateway_memory import InMemoryProductoGateway


def test_get_productos_compra_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.producto_compra_gateway = InMemoryProductoGateway()
    data = producto_compra_list()
    assert "items" in data
    assert isinstance(data["items"], list)
