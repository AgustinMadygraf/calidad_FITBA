import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.catalogos import moneda_get, moneda_list
from src.infrastructure.memory.moneda_gateway_memory import InMemoryMonedaGateway


def test_get_monedas_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.moneda_gateway = InMemoryMonedaGateway()
    data = moneda_list()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any(item.get("nombre") == "Pesos Argentinos" for item in data["items"])


def test_get_moneda_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    gateway_provider.moneda_gateway = InMemoryMonedaGateway()
    item = moneda_get(0)
    assert item["ID"] == 0
    assert item["codigo"] == "string"
