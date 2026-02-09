from src.infrastructure.httpx.token_gateway_httpx import HttpxTokenGateway


def test_token_gateway_returns_status(monkeypatch):
    def fake_status(*_args, **_kwargs):
        return {"token_preview": "abc", "expires_in_seconds": 10, "expires_at": 1, "from_cache": True}

    monkeypatch.setattr(
        "src.infrastructure.httpx.token_gateway_httpx.get_token_status", fake_status
    )
    gw = HttpxTokenGateway()
    status = gw.get_status()
    assert status["token_preview"] == "abc"
