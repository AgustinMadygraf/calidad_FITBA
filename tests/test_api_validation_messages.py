from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app


def test_lista_precio_path_id_validation_message_is_human_friendly():
    client = TestClient(app)
    response = client.get("/API/1.1/listaPrecioBean/{id}")
    assert response.status_code == 422
    assert "Parametro de ruta invalido" in response.json().get("detail", "")
    assert "/API/1.1/listaPrecioBean/1" in response.json().get("detail", "")
