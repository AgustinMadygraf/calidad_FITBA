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


def test_collect_product_payload_rejects_empty_payload():
    outputs = []
    payload = run_cli.collect_product_payload(
        _input_from(["", "", "", ""]),
        outputs.append,
    )

    assert payload is None
    assert outputs
    assert run_cli.EMPTY_PRODUCT_PAYLOAD_MESSAGE in outputs[0]


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


def test_collect_product_payload_rejects_empty_json_object():
    outputs = []
    payload = run_cli.collect_product_payload(
        _input_from(["", "", "", "{}"]),
        outputs.append,
    )

    assert payload is None
    assert outputs
    assert run_cli.EMPTY_PRODUCT_PAYLOAD_MESSAGE in outputs[0]


def test_normalize_entity_accepts_only_official_entity_names():
    assert run_cli.normalize_entity("ProductoVentaBean") == run_cli.PRODUCT_ENTITY
    assert run_cli.normalize_entity("clienteBean") == "clienteBean"
    assert run_cli.normalize_entity("1") is None
    assert run_cli.normalize_entity("4") is None
    assert run_cli.normalize_entity("product") is None


def test_post_product_success(monkeypatch):
    captured = {}

    def fake_post(method, url, *, json, timeout):
        captured["method"] = method
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse(200, {"productoid": 1, "nombre": "P1"})

    monkeypatch.setattr(run_cli, "request_with_token", fake_post)

    result = run_cli.post_product(
        "http://localhost:8000", {"nombre": "P1"}, timeout=7.5
    )

    assert result.ok is True
    assert result.status_code == 200
    assert result.payload == {"productoid": 1, "nombre": "P1"}
    assert captured["method"] == "POST"
    assert captured["url"] == "http://localhost:8000/API/1.1/ProductoVentaBean"
    assert captured["json"] == {"nombre": "P1"}
    assert captured["timeout"] == 7.5


def test_post_product_forbidden_in_read_only_mode(monkeypatch):
    def fake_post(method, url, *, json, timeout):
        return DummyResponse(403, {"detail": "Read-only mode"})

    monkeypatch.setattr(run_cli, "request_with_token", fake_post)

    result = run_cli.post_product(
        "http://localhost:8000", {"nombre": "P1"}, timeout=5.0
    )

    assert result.ok is False
    assert result.status_code == 403
    assert "token OAuth2" in result.message


def test_post_product_reports_oauth_runtime_error(monkeypatch):
    def fake_post(method, url, *, json, timeout):
        raise RuntimeError("TokenEndpoint error 401")

    monkeypatch.setattr(run_cli, "request_with_token", fake_post)

    result = run_cli.post_product(
        "https://xubio.com", {"nombre": "P1"}, timeout=5.0
    )

    assert result.ok is False
    assert result.status_code is None
    assert "Error OAuth2" in result.message


def test_process_command_create_uses_current_entity(monkeypatch):
    outputs = []
    state = run_cli.CLIState(current_entity=run_cli.PRODUCT_ENTITY)

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


def test_process_command_create_rejects_empty_payload_without_post(monkeypatch):
    outputs = []
    state = run_cli.CLIState(current_entity=run_cli.PRODUCT_ENTITY)
    called = {"post": False}

    monkeypatch.setattr(run_cli, "collect_product_payload", lambda _ri, _wo: {})

    def _should_not_post(_base_url, _payload, _timeout):
        called["post"] = True
        return run_cli.PostResult(
            ok=True,
            status_code=200,
            message="NO_DEBERIA_OCURRIR",
            payload=None,
        )

    monkeypatch.setattr(run_cli, "post_product", _should_not_post)

    should_exit = run_cli.process_command(
        "CREATE",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )

    assert should_exit is False
    assert called["post"] is False
    assert outputs
    assert outputs[0] == run_cli.EMPTY_PRODUCT_PAYLOAD_MESSAGE


def test_expand_numeric_selection_rejects_numeric_shortcuts():
    outputs = []
    state = run_cli.CLIState()
    expanded = run_cli._expand_numeric_selection(
        "1",
        state,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )
    assert expanded is None
    assert outputs
    assert "Atajos numericos deshabilitados" in outputs[0]


def test_expand_numeric_selection_rejects_function_key_shortcuts():
    outputs = []
    state = run_cli.CLIState()
    expanded = run_cli._expand_numeric_selection(
        "F12",
        state,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )
    assert expanded is None
    assert outputs
    assert "Atajos function-key legacy deshabilitados" in outputs[0]


def test_expand_numeric_selection_passthrough_for_textual_commands():
    outputs = []
    state = run_cli.CLIState()
    expanded = run_cli._expand_numeric_selection(
        "CREATE ProductoVentaBean",
        state,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )
    assert expanded == "CREATE ProductoVentaBean"
    assert outputs == []


def test_process_command_numeric_shortcut_is_rejected(monkeypatch):
    outputs = []
    state = run_cli.CLIState(current_entity=run_cli.PRODUCT_ENTITY)
    called = {"post": False}

    monkeypatch.setattr(
        run_cli,
        "collect_product_payload",
        lambda _read_input, _write_output: {"nombre": "P1"},
    )

    def _should_not_post(_base_url, _payload, _timeout):
        called["post"] = True
        return run_cli.PostResult(
            ok=True,
            status_code=200,
            message="NO_DEBERIA_OCURRIR",
            payload=None,
        )

    monkeypatch.setattr(run_cli, "post_product", _should_not_post)

    should_exit = run_cli.process_command(
        "3",
        state,
        "https://xubio.com",
        10.0,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )

    assert should_exit is False
    assert called["post"] is False
    assert outputs
    assert "Atajos numericos deshabilitados" in outputs[0]


def test_process_command_abbreviation_cr_runs_create_flow(monkeypatch):
    outputs = []
    state = run_cli.CLIState(current_entity=run_cli.PRODUCT_ENTITY)

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
        "CR",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )

    assert should_exit is False
    assert outputs[0] == "Producto creado"


def test_process_command_abbreviation_dlt_maps_delete_stub():
    outputs = []
    state = run_cli.CLIState(current_entity="clienteBean")
    should_exit = run_cli.process_command(
        "DLT",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert outputs[0] == "MVP: DELETE clienteBean esta en modo stub."


def test_process_command_abbreviation_dsp_routes_to_get_with_id():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "DSP ProductoVentaBean 55",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert outputs[0] == "MVP: GET ProductoVentaBean esta en modo stub."


def test_process_command_abbreviation_dsp_no_args_uses_current_entity():
    outputs = []
    state = run_cli.CLIState(current_entity="clienteBean")
    should_exit = run_cli.process_command(
        "DSP",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert outputs[0] == "MVP: LIST clienteBean esta en modo stub."


def test_process_command_abbreviation_dsp_no_args_without_context_shows_menu():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "DSP",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert "XUBIO CLI (MVP)" in outputs[0]


def test_process_command_function_key_shortcut_is_rejected():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "F3",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert "Atajos function-key legacy deshabilitados" in outputs[0]


def test_process_command_exit_aliases():
    state = run_cli.CLIState()
    assert run_cli.process_command("QUIT", state, "https://xubio.com", 10.0) is True
    assert run_cli.process_command("SALIR", state, "https://xubio.com", 10.0) is True


def test_process_command_help_alias_renders_menu():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "HELP",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert "XUBIO CLI (MVP)" in outputs[0]


def test_process_command_unknown_command_suggests_closest_match():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "meny",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert "Quisiste decir MENU?" in outputs[0]


def test_process_command_unknown_command_without_close_match():
    outputs = []
    state = run_cli.CLIState()
    should_exit = run_cli.process_command(
        "zzzzz",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )
    assert should_exit is False
    assert outputs
    assert outputs[0] == "Comando no reconocido: ZZZZZ. Usa HELP para ayuda."


def test_process_command_enter_rejects_entity_number():
    outputs = []
    state = run_cli.CLIState()

    should_exit = run_cli.process_command(
        "ENTER 2",
        state,
        "https://xubio.com",
        10.0,
        write_output=outputs.append,
    )

    assert should_exit is False
    assert state.current_entity is None
    assert outputs
    assert "Entity type no soportado" in outputs[0]


def test_render_menu_includes_status_line():
    state = run_cli.CLIState(last_status="Operacion completada")
    rendered = run_cli.render_menu(state, "https://xubio.com")
    assert "Estado: Operacion completada" in rendered


def test_render_menu_includes_abbreviation_help():
    rendered = run_cli.render_menu(run_cli.CLIState(), "https://xubio.com")
    assert "Abreviaturas: CR=CREATE DLT=DELETE DSP=LIST/GET" in rendered
    assert "Atajos numericos/function-key: deshabilitados" in rendered


def test_prompt_for_uses_cli_style():
    assert run_cli.prompt_for(run_cli.CLIState()) == "xubio[menu]> "
    assert run_cli.prompt_for(run_cli.CLIState(current_entity="clienteBean")) == "xubio[clienteBean]> "
