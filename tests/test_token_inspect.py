from src.infrastructure.fastapi import api


class FakeTokenGateway:
    def __init__(self, payload):
        self._payload = payload

    def get_status(self):
        return self._payload


def test_token_inspect_ok(monkeypatch):
    monkeypatch.setattr(
        api,
        "token_gateway",
        FakeTokenGateway(
            {"token_preview": "abc", "expires_in_seconds": 10, "expires_at": 1, "from_cache": True}
        ),
    )
    data = api.token_inspect()
    assert data["token_preview"] == "abc"


def test_token_inspect_value_error(monkeypatch):
    class ErrGateway:
        def get_status(self):
            raise ValueError("bad")

    monkeypatch.setattr(api, "token_gateway", ErrGateway())
    try:
        api.token_inspect()
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 400
    else:
        raise AssertionError("Expected HTTPException 400")
