from src.infrastructure.memory.categoria_fiscal_gateway_memory import (
    InMemoryCategoriaFiscalGateway,
)
from src.infrastructure.memory.identificacion_tributaria_gateway_memory import (
    InMemoryIdentificacionTributariaGateway,
)
from src.infrastructure.memory.moneda_gateway_memory import InMemoryMonedaGateway
from src.infrastructure.memory.vendedor_gateway_memory import InMemoryVendedorGateway


def test_categoria_fiscal_get_supports_lowercase_id_key():
    gateway = InMemoryCategoriaFiscalGateway(items=[{"id": 77, "codigo": "X"}])
    item = gateway.get(77)
    assert item is not None
    assert item["id"] == 77


def test_categoria_fiscal_get_returns_none_when_missing():
    gateway = InMemoryCategoriaFiscalGateway(items=[{"id": 77, "codigo": "X"}])
    assert gateway.get(999) is None


def test_identificacion_tributaria_get_supports_lowercase_id_key():
    gateway = InMemoryIdentificacionTributariaGateway(items=[{"id": 55, "codigo": "DNI"}])
    item = gateway.get(55)
    assert item is not None
    assert item["id"] == 55


def test_identificacion_tributaria_get_returns_none_when_missing():
    gateway = InMemoryIdentificacionTributariaGateway(items=[{"id": 55, "codigo": "DNI"}])
    assert gateway.get(999) is None


def test_moneda_get_supports_lowercase_id_key():
    gateway = InMemoryMonedaGateway(items=[{"id": 2, "nombre": "USD", "codigo": "USD"}])
    item = gateway.get(2)
    assert item is not None
    assert item["id"] == 2


def test_moneda_get_returns_none_when_missing():
    gateway = InMemoryMonedaGateway(items=[{"id": 2, "nombre": "USD", "codigo": "USD"}])
    assert gateway.get(999) is None


def test_vendedor_get_supports_vendedor_id_key():
    gateway = InMemoryVendedorGateway(items=[{"vendedorId": 3, "nombre": "Ana"}])
    item = gateway.get(3)
    assert item is not None
    assert item["vendedorId"] == 3


def test_vendedor_get_supports_uppercase_id_key():
    gateway = InMemoryVendedorGateway(items=[{"ID": 4, "nombre": "Luis"}])
    item = gateway.get(4)
    assert item is not None
    assert item["ID"] == 4


def test_vendedor_get_supports_lowercase_id_key():
    gateway = InMemoryVendedorGateway(items=[{"id": 5, "nombre": "Marta"}])
    item = gateway.get(5)
    assert item is not None
    assert item["id"] == 5


def test_vendedor_get_returns_none_when_missing():
    gateway = InMemoryVendedorGateway(items=[{"vendedorId": 3, "nombre": "Ana"}])
    assert gateway.get(999) is None
