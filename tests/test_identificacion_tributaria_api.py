import os

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.catalogos import (
    identificacion_tributaria_get,
    identificacion_tributaria_list,
)
from src.infrastructure.memory.identificacion_tributaria_gateway_memory import (
    InMemoryIdentificacionTributariaGateway,
)


def test_get_identificaciones_tributarias_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    gateway_provider.identificacion_tributaria_gateway = (
        InMemoryIdentificacionTributariaGateway()
    )
    data = identificacion_tributaria_list()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any(item.get("codigo") == "CUIT" for item in data["items"])


def test_get_identificacion_tributaria_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    gateway_provider.identificacion_tributaria_gateway = (
        InMemoryIdentificacionTributariaGateway()
    )
    item = identificacion_tributaria_get(41)
    assert item["ID"] == 41
    assert item["codigo"] == "ACTA_NACIMIENTO"
