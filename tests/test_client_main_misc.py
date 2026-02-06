from __future__ import annotations

import builtins

import pytest

import src.client.app.main as main_module


def test_prompt_handles_eof(monkeypatch) -> None:
    def fake_input(_):
        raise EOFError()

    monkeypatch.setattr(builtins, "input", fake_input)
    with pytest.raises(SystemExit):
        main_module._prompt(">")


def test_apply_theme_and_clear(capsys) -> None:
    themed = main_module._apply_theme("X")
    assert "X" in themed
    main_module._clear()
    captured = capsys.readouterr()
    assert captured.out != ""


def test_main_menu_body() -> None:
    body = main_module._main_menu_body()
    assert "PRODUCTO" in body


def test_is_prod_enabled_override(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_IS_PROD_OVERRIDE", True)
    assert main_module._is_prod_enabled() is True


def test_render_screen_and_single_page(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_term_width", lambda min_width=60: 60)
    monkeypatch.setattr(main_module, "_pause", lambda: None)
    main_module._render_screen("TITLE", "line1\nline2", "footer")
    main_module._render_paginated_screen("TITLE", "line1")


def test_field_prompt_default(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_prompt", lambda _: "")
    assert main_module._field_prompt("SKU", required=False, default="DEF") == "DEF"


def test_read_price_valid(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_prompt", lambda _: "10.5")
    assert main_module._read_price() == 10.5
