import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.catalogos import (
    circuito_contable_get,
    circuito_contable_list,
)
from src.infrastructure.memory.circuito_contable_gateway_memory import (
    InMemoryCircuitoContableGateway,
)


def test_get_circuitos_contables_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.circuito_contable_gateway = InMemoryCircuitoContableGateway()
    data = circuito_contable_list()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any(item.get("nombre") == "string" for item in data["items"])


def test_get_circuito_contable_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    gateway_provider.circuito_contable_gateway = InMemoryCircuitoContableGateway()
    item = circuito_contable_get(0)
    assert item["circuitoContable_id"] == 0
    assert item["codigo"] == "string"
