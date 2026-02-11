import os

from src.infrastructure.fastapi.api import (
    app as global_app,
)
from src.infrastructure.fastapi.api import categoria_fiscal_get, categoria_fiscal_list
from src.infrastructure.memory.categoria_fiscal_gateway_memory import (
    InMemoryCategoriaFiscalGateway,
)


def test_get_categorias_fiscales_returns_wrapper():
    os.environ["IS_PROD"] = "false"
    global_app.categoria_fiscal_gateway = InMemoryCategoriaFiscalGateway()
    data = categoria_fiscal_list()
    assert "items" in data
    assert isinstance(data["items"], list)
    assert any(item.get("codigo") == "RI" for item in data["items"])


def test_get_categoria_fiscal_by_id_returns_item():
    os.environ["IS_PROD"] = "false"
    global_app.categoria_fiscal_gateway = InMemoryCategoriaFiscalGateway()
    item = categoria_fiscal_get(1)
    assert item["ID"] == 1
    assert item["codigo"] == "RI"
