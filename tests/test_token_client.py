import httpx

from src.infrastructure.httpx.token_client import is_invalid_token_response


def test_invalid_token_true_for_error_dict():
    resp = httpx.Response(401, json={"error": "invalid_token"})
    assert is_invalid_token_response(resp) is True


def test_invalid_token_false_for_list_payload():
    resp = httpx.Response(200, json=[{"ok": True}])
    assert is_invalid_token_response(resp) is False
