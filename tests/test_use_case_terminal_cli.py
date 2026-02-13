from src.use_cases import terminal_cli


def test_build_product_payload_minimal():
    result = terminal_cli.build_product_payload(
        nombre="P1",
        codigo="",
        usrcode="",
        extra_json="",
    )
    assert result.error_message is None
    assert result.payload == {"nombre": "P1"}


def test_build_product_payload_merges_extra_json():
    result = terminal_cli.build_product_payload(
        nombre="P1",
        codigo="COD-1",
        usrcode="",
        extra_json='{"activo": 1}',
    )
    assert result.error_message is None
    assert result.payload == {"nombre": "P1", "codigo": "COD-1", "activo": 1}


def test_build_product_payload_rejects_invalid_json():
    result = terminal_cli.build_product_payload(
        nombre="P1",
        codigo="",
        usrcode="",
        extra_json="{",
    )
    assert result.payload is None
    assert result.error_message is not None
    assert "JSON invalido" in result.error_message


def test_build_product_payload_rejects_non_object_json():
    result = terminal_cli.build_product_payload(
        nombre="",
        codigo="",
        usrcode="",
        extra_json='["x"]',
    )
    assert result.payload is None
    assert result.error_message == "payload_json debe ser un objeto JSON."


def test_build_product_payload_rejects_empty_payload():
    result = terminal_cli.build_product_payload(
        nombre="",
        codigo="",
        usrcode="",
        extra_json="",
    )
    assert result.payload is None
    assert result.error_message == terminal_cli.EMPTY_PRODUCT_PAYLOAD_MESSAGE


def test_enter_entity_requires_argument():
    state = terminal_cli.CLIState()
    result = terminal_cli.enter_entity([], state)
    assert result.ok is False
    assert result.message == "Uso: ENTER <entity_type>"
    assert state.current_entity is None


def test_enter_entity_rejects_invalid_entity():
    state = terminal_cli.CLIState()
    result = terminal_cli.enter_entity(["producto"], state)
    assert result.ok is False
    assert "Entity type no soportado" in result.message
    assert state.current_entity is None


def test_enter_entity_sets_context():
    state = terminal_cli.CLIState()
    result = terminal_cli.enter_entity(["2"], state)
    assert result.ok is True
    assert result.message == "Contexto actual: clienteBean"
    assert state.current_entity == "clienteBean"


def test_plan_entity_action_requires_entity_when_no_context():
    state = terminal_cli.CLIState()
    plan = terminal_cli.plan_entity_action("LIST", [], state)
    assert plan.ok is False
    assert plan.error_message == "Debes indicar entity_type o usar ENTER <entity_type>."


def test_plan_entity_action_rejects_invalid_entity():
    state = terminal_cli.CLIState()
    plan = terminal_cli.plan_entity_action("LIST", ["foo"], state)
    assert plan.ok is False
    assert plan.error_message is not None
    assert "Entity type no soportado" in plan.error_message


def test_plan_entity_action_detects_create_product_path():
    state = terminal_cli.CLIState(current_entity=terminal_cli.PRODUCT_ENTITY)
    plan = terminal_cli.plan_entity_action("CREATE", [], state)
    assert plan.ok is True
    assert plan.target_entity == terminal_cli.PRODUCT_ENTITY
    assert plan.is_create_product is True


def test_plan_entity_action_stub_for_non_product_create():
    state = terminal_cli.CLIState(current_entity="clienteBean")
    plan = terminal_cli.plan_entity_action("CREATE", [], state)
    assert plan.ok is True
    assert plan.target_entity == "clienteBean"
    assert plan.is_create_product is False


def test_resolve_alias_command_maps_dsp_variants():
    state_without_ctx = terminal_cli.CLIState()
    state_with_ctx = terminal_cli.CLIState(current_entity="clienteBean")

    command, args = terminal_cli.resolve_alias_command("DSP", [], state_without_ctx)
    assert command == "MENU"
    assert args == []

    command, args = terminal_cli.resolve_alias_command("DSP", [], state_with_ctx)
    assert command == "LIST"
    assert args == ["clienteBean"]

    command, args = terminal_cli.resolve_alias_command("DSP", ["1"], state_without_ctx)
    assert command == "LIST"
    assert args == ["1"]

    command, args = terminal_cli.resolve_alias_command("DSP", ["1", "55"], state_without_ctx)
    assert command == "GET"
    assert args == ["1", "55"]


def test_expand_numeric_selection_supports_function_keys_and_invalid_options():
    outputs = []
    state = terminal_cli.CLIState()
    expanded = terminal_cli.expand_numeric_selection(
        "f1",
        state,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )
    assert expanded == "MENU"
    assert outputs == []

    expanded = terminal_cli.expand_numeric_selection(
        "10",
        state,
        read_input=lambda _prompt: "",
        write_output=outputs.append,
    )
    assert expanded is None
    assert outputs
    assert "Opcion numerica invalida" in outputs[0]
