from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app


def test_lista_precio_detail_openapi_has_fixed_example():
    client = TestClient(app)
    schema = client.get("/openapi.json").json()
    path = schema["paths"]["/API/1.1/listaPrecioBean/{lista_precio_id}"]["get"]
    example = path["responses"]["200"]["content"]["application/json"]["example"]
    assert "listaPrecioID" in example
    assert "listaPrecioItem" in example
    assert example["moneda"]["nombre"] == "Pesos Argentinos"
