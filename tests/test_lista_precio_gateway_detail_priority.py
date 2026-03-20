import httpx

from src.infrastructure.httpx.lista_precio_gateway_xubio import XubioListaPrecioGateway


def test_get_prefers_detail_over_item_cache_seeded_by_list(monkeypatch):
    calls = {"detail": 0}

    def fake_request(method, url, **kwargs):
        if method == "GET" and url.endswith("/API/1.1/listaPrecioBean"):
            return httpx.Response(
                200,
                json=[{"listaPrecioID": 9797, "nombre": "tinta", "listaPrecioItem": []}],
            )
        if method == "GET" and url.endswith("/API/1.1/listaPrecioBean/9797"):
            calls["detail"] += 1
            return httpx.Response(
                200,
                json={
                    "listaPrecioID": 9797,
                    "nombre": "tinta",
                    "listaPrecioItem": [{"codigo": "TINTA"}],
                },
            )
        raise AssertionError(f"unexpected call: {method} {url}")

    monkeypatch.setattr(
        "src.infrastructure.httpx.xubio_crud_helpers.request_with_token",
        fake_request,
    )

    gw = XubioListaPrecioGateway(base_url="https://xubio.com")
    listed = gw.list()
    assert listed[0]["listaPrecioItem"] == []
    detailed = gw.get(9797)
    assert detailed["listaPrecioItem"] == [{"codigo": "TINTA"}]
    assert calls["detail"] == 1
