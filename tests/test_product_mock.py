from __future__ import annotations


def test_create_get_product(client) -> None:
    create_resp = client.post(
        "/terminal/execute",
        json={
            "session_id": "test",
            "command": "CREATE product",
            "args": {"external_id": "p-1", "name": "Producto A", "price": 10.5},
        },
    )
    assert create_resp.status_code == 200
    assert "Producto creado" in create_resp.json()["screen"]

    get_resp = client.post(
        "/terminal/execute",
        json={
            "session_id": "test",
            "command": "GET product",
            "args": {"external_id": "p-1"},
        },
    )
    assert get_resp.status_code == 200
    screen = get_resp.json()["screen"]
    assert "Producto:" in screen
    assert "Producto A" in screen
