from typing import Callable, List

import run_cli


class DummyResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if self._payload is None:
            raise ValueError("no json payload")
        return self._payload


def _input_from(values: List[str]) -> Callable[[str], str]:
    iterator = iter(values)

    def _read(_: str) -> str:
        return next(iterator)

    return _read


def test_collect_product_payload_minimal():
    outputs = []
    payload = run_cli.collect_product_payload(
        _input_from(["P1", "", "", ""]),
        outputs.append,
    )

    assert payload == {"nombre": "P1"}
    assert outputs == []


def test_collect_product_payload_with_extra_json():
    outputs = []
    payload = run_cli.collect_product_payload(
        _input_from(["P1", "COD-1", "", '{"activo": 1}']),
        outputs.append,
    )

    assert payload == {"nombre": "P1", "codigo": "COD-1", "activo": 1}
    assert outputs == []


def test_collect_product_payload_rejects_invalid_json():
    outputs = []
    payload = run_cli.collect_product_payload(
        _input_from(["P1", "", "", "{"]),
        outputs.append,
    )

    assert payload is None
    assert outputs
    assert "JSON invalido" in outputs[0]


def test_post_product_success(monkeypatch):
    captured = {}

    def fake_post(url, *, json, timeout):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse(200, {"productoid": 1, "nombre": "P1"})

    monkeypatch.setattr(run_cli.httpx, "post", fake_post)

    result = run_cli.post_product(
        "http://localhost:8000", {"nombre": "P1"}, timeout=7.5
    )

    assert result.ok is True
    assert result.status_code == 200
    assert result.payload == {"productoid": 1, "nombre": "P1"}
    assert captured["url"] == "http://localhost:8000/API/1.1/ProductoVentaBean"
    assert captured["json"] == {"nombre": "P1"}
    assert captured["timeout"] == 7.5


def test_post_product_forbidden_in_read_only_mode(monkeypatch):
    def fake_post(url, *, json, timeout):
        return DummyResponse(403, {"detail": "Read-only mode"})

    monkeypatch.setattr(run_cli.httpx, "post", fake_post)

    result = run_cli.post_product(
        "http://localhost:8000", {"nombre": "P1"}, timeout=5.0
    )

    assert result.ok is False
    assert result.status_code == 403
    assert "IS_PROD=true" in result.message


def test_process_command_create_uses_current_entity(monkeypatch):
    outputs = []
    state = run_cli.CLIState(current_entity="product")

    monkeypatch.setattr(
        run_cli,
        "collect_product_payload",
        lambda _read_input, _write_output: {"nombre": "P1"},
    )
    monkeypatch.setattr(
        run_cli,
        "post_product",
        lambda _base_url, _payload, _timeout: run_cli.PostResult(
            ok=True,
            status_code=200,
            message="Producto creado",
            payload={"productoid": 1},
        ),
    )

    should_exit = run_cli.process_command(
        "CREATE",
        state,
        "http://localhost:8000",
        10.0,
        read_input=lambda _: "",
        write_output=outputs.append,
    )

    assert should_exit is False
    assert outputs[0] == "Producto creado"
    assert '"productoid": 1' in outputs[1]
