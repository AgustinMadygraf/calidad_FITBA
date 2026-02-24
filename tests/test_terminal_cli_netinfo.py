from src.interface_adapter.controllers import terminal_cli


def test_process_command_netinfo_renders_diagnostics(monkeypatch):
    outputs = []
    state = terminal_cli.CLIState()

    monkeypatch.setattr(terminal_cli, "_detect_lan_ips", lambda: ["10.176.61.33"])
    monkeypatch.setattr(
        terminal_cli,
        "_is_tcp_open",
        lambda host, port, timeout=0.25: True if port == 8000 else False,
    )

    should_exit = terminal_cli.process_command(
        "NETINFO",
        state,
        "https://api.empresa.local",
        10.0,
        write_output=outputs.append,
    )

    assert should_exit is False
    assert outputs
    out = outputs[0]
    assert "Diagnostico de red y HTTPS" in out
    assert "IPs LAN detectadas: 10.176.61.33 (privada)" in out
    assert "Base URL esquema: HTTPS" in out
    assert "Base URL puerto: 443" in out
    assert "Puerto local 8000 abierto: si" in out
    assert "Puerto local 443 abierto: no" in out


def test_process_command_red_alias_maps_to_netinfo(monkeypatch):
    outputs = []
    state = terminal_cli.CLIState()

    monkeypatch.setattr(terminal_cli, "_detect_lan_ips", lambda: [])
    monkeypatch.setattr(terminal_cli, "_is_tcp_open", lambda *_args, **_kwargs: False)

    should_exit = terminal_cli.process_command(
        "RED",
        state,
        "http://10.176.61.33:8000",
        10.0,
        write_output=outputs.append,
    )

    assert should_exit is False
    assert outputs
    out = outputs[0]
    assert "Diagnostico de red y HTTPS" in out
    assert "Base URL esquema: HTTP" in out
    assert "Base URL puerto: 8000" in out
