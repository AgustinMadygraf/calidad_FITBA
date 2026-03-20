import json
from pathlib import Path

from src.infrastructure.fastapi.gateway_provider import gateway_provider
from src.infrastructure.fastapi.routers.comprobante_venta import comprobante_venta_get
from src.infrastructure.memory.comprobante_venta_gateway_memory import (
    InMemoryComprobanteVentaGateway,
)
from src.interface_adapter.mappers.comprobante_venta_contract import _CONTRACT_FIELDS


def _load_fixture(name: str):
    base = Path(__file__).parent / "fixtures" / "comprobante_venta"
    return json.loads((base / name).read_text(encoding="utf-8"))


def test_comprobante_venta_contract_matches_xubio_fixture():
    replica_input = _load_fixture("fixture_replica_input.json")
    expected = _load_fixture("fixture_api.json")
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway(
        items=[replica_input]
    )

    output = comprobante_venta_get(expected["transaccionid"])

    assert output == expected


def test_comprobante_venta_contract_has_required_keys_and_arrays():
    replica_input = {
        "transaccionid": 700,
        "cae": "abc",
    }
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway(
        items=[replica_input]
    )

    output = comprobante_venta_get(700)

    assert set(output.keys()) == set(_CONTRACT_FIELDS)
    assert output["transaccionProductoItems"] == []
    assert output["transaccionPercepcionItems"] == []
    assert output["transaccionCobranzaItems"] == []
    assert output["caefechaVto"] == []


def test_comprobante_venta_contract_exposes_both_cae_keys():
    replica_input = {
        "transaccionid": 701,
        "cae": "999",
        "caefechaVto": [2026, 1, 10],
    }
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway(
        items=[replica_input]
    )

    output = comprobante_venta_get(701)

    assert output["CAE"] == "999"
    assert output["cae"] == "999"
    assert output["caefechaVto"] == [2026, 1, 10]


def test_comprobante_venta_contract_coerces_scalar_fields_from_object():
    replica_input = {
        "transaccionid": 702,
        "tipo": {"ID": 1, "nombre": "x"},
        "condicionDePago": {"id": 2},
    }
    gateway_provider.comprobante_venta_gateway = InMemoryComprobanteVentaGateway(
        items=[replica_input]
    )

    output = comprobante_venta_get(702)

    assert output["tipo"] == 1
    assert output["condicionDePago"] == 2
