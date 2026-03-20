from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app
from src.infrastructure.fastapi.gateway_provider import gateway_provider


class _StubListaPrecioGateway:
    def get(self, _lista_precio_id: int):
        return {
            "listaPrecioID": 9797,
            "activo": True,
            "nombre": "Minorista",
            "descripcion": "Base",
            "esDefault": False,
            "moneda": {"ID": -2, "id": -2},
            "tipo": 1,
            "iva": 0,
            "listaPrecioItem": [
                {
                    "listaPrecioID": 9797,
                    "producto": {"ID": 1, "nombre": "P1", "codigo": "", "id": 1},
                    "precio": 10,
                    "codigo": "TINTA",
                    "referencia": 0,
                }
            ],
            "ocultarSinPrecio": False,
        }

    def list(self):
        return []


def test_lista_precio_detail_handles_incomplete_upstream_payload():
    original = gateway_provider.lista_precio_gateway
    gateway_provider.lista_precio_gateway = _StubListaPrecioGateway()
    try:
        client = TestClient(app)
        response = client.get("/API/1.1/listaPrecioBean/9797")
        assert response.status_code == 200
        body = response.json()
        assert body["moneda"] == {"ID": -2, "id": -2}
        assert "listaReferencia" not in body or body["listaReferencia"] is None
        assert len(body["listaPrecioItem"]) == 1
        assert body["listaPrecioItem"][0]["codigo"] == "TINTA"
    finally:
        gateway_provider.lista_precio_gateway = original
