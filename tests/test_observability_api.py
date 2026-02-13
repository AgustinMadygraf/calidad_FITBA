import json

from fastapi.testclient import TestClient

from src.infrastructure.fastapi.api import app
from src.infrastructure.fastapi.routers import observability


def _valid_http_request_event():
    return {
        "type": "http_request",
        "level": "info",
        "timestamp": "2026-02-13T12:00:00.000Z",
        "context": {
            "method": "GET",
            "url": "/API/1.1/remitoVentaBean",
            "durationMs": 182.33,
            "status": 200,
            "outcome": "success",
            "errorName": None,
        },
    }


def setup_function():
    observability._reset_observability_state_for_tests()


def teardown_function():
    observability._reset_observability_state_for_tests()


def test_observability_accepts_and_persists_http_request_event():
    client = TestClient(app)
    response = client.post("/observability/events", json=_valid_http_request_event())

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "accepted"
    assert body["requestId"]

    items = observability._events_snapshot_for_tests()
    assert len(items) == 1
    assert items[0]["eventType"] == "http_request"
    assert items[0]["level"] == "info"
    assert items[0]["requestId"] == body["requestId"]


def test_observability_truncates_long_frontend_error_stack():
    long_stack = "X" * (observability.MAX_STACK_BYTES + 1024)
    payload = {
        "type": "frontend_error",
        "level": "error",
        "timestamp": "2026-02-13T12:00:00.000Z",
        "context": {
            "source": "window_error",
            "message": "boom",
            "errorName": "TypeError",
            "stack": long_stack,
        },
    }

    client = TestClient(app)
    response = client.post("/observability/events", json=payload)

    assert response.status_code == 202
    items = observability._events_snapshot_for_tests()
    assert len(items) == 1
    stored_stack = items[0]["context"]["stack"]
    assert isinstance(stored_stack, str)
    assert len(stored_stack.encode("utf-8")) <= observability.MAX_STACK_BYTES


def test_observability_returns_400_for_invalid_type():
    payload = _valid_http_request_event()
    payload["type"] = "otro_evento"
    client = TestClient(app)

    response = client.post("/observability/events", json=payload)

    assert response.status_code == 400
    body = response.json()
    assert "type invalido" in body["detail"]
    assert body["requestId"]


def test_observability_returns_415_for_non_json_content_type():
    payload = json.dumps(_valid_http_request_event())
    client = TestClient(app)

    response = client.post(
        "/observability/events",
        content=payload,
        headers={"Content-Type": "text/plain"},
    )

    assert response.status_code == 415
    body = response.json()
    assert body["requestId"]


def test_observability_returns_413_for_too_large_body():
    huge_context = {"stack": "X" * (observability.MAX_EVENT_BODY_BYTES + 1024)}
    payload = json.dumps(
        {
            "type": "frontend_error",
            "level": "error",
            "timestamp": "2026-02-13T12:00:00.000Z",
            "context": huge_context,
        }
    )
    client = TestClient(app)

    response = client.post(
        "/observability/events",
        content=payload,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 413
    body = response.json()
    assert body["requestId"]


def test_observability_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(observability, "RATE_LIMIT_MAX_REQUESTS", 1)
    client = TestClient(app)
    payload = _valid_http_request_event()

    first = client.post("/observability/events", json=payload)
    second = client.post("/observability/events", json=payload)

    assert first.status_code == 202
    assert second.status_code == 429
    assert second.json()["requestId"]


def test_observability_logs_include_request_id_and_result(caplog):
    client = TestClient(app)
    payload = _valid_http_request_event()

    with caplog.at_level("INFO"):
        response = client.post("/observability/events", json=payload)

    assert response.status_code == 202
    assert any(
        "observability accepted request_id=" in record.message for record in caplog.records
    )


def test_observability_cors_preflight_allows_configured_origin():
    client = TestClient(app)
    response = client.options(
        "/observability/events",
        headers={
            "Origin": "http://127.0.0.1:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:5173"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
    assert "content-type" in response.headers.get(
        "access-control-allow-headers", ""
    ).lower()


def test_observability_cors_preflight_rejects_other_origin():
    client = TestClient(app)
    response = client.options(
        "/observability/events",
        headers={
            "Origin": "http://127.0.0.1:5174",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 400
    assert response.headers.get("access-control-allow-origin") is None
