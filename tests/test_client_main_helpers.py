from __future__ import annotations

import shutil

import pytest

import src.client.app.main as main_module


def test_parse_bool_option() -> None:
    assert main_module._parse_bool_option("true") is True
    assert main_module._parse_bool_option("0") is False
    assert main_module._parse_bool_option(None) is None
    assert main_module._parse_bool_option("  ") is None
    with pytest.raises(Exception):
        main_module._parse_bool_option("maybe")


def test_fit_text() -> None:
    assert main_module._fit_text("abc", 5) == "abc  "
    assert main_module._fit_text("abcdef", 3) == "abc"
    assert main_module._fit_text("abcdef", 4) == "a..."


def test_term_dimensions(monkeypatch) -> None:
    monkeypatch.setattr(shutil, "get_terminal_size", lambda fallback=None: shutil.os.terminal_size((40, 10)))
    assert main_module._term_width(60) == 60
    assert main_module._term_height(20) == 20


def test_status_line(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_CURRENT_SESSION_ID", "abcdef123456")
    monkeypatch.setattr(main_module, "_IS_PROD_OVERRIDE", True)

    class _FakeDT:
        @classmethod
        def now(cls):  # noqa: N805 - matches datetime API
            class _Inner:
                def strftime(self, fmt: str) -> str:
                    _ = fmt
                    return "2024-01-02 03:04:05"

            return _Inner()

    monkeypatch.setattr(main_module, "datetime", _FakeDT)

    status = main_module._status_line()
    assert "MODO:PROD" in status
    assert "SESION:abcdef12" in status
    assert "2024-01-02 03:04:05" in status
