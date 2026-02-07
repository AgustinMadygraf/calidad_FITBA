from __future__ import annotations

import pytest

from src.interface_adapter.controller.cli.settings import ClientSettings
from src.server.app.settings import Settings


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_settings_bool_parsing(value: str, expected: bool) -> None:
    settings = Settings(IS_PROD=value)
    assert settings.IS_PROD is expected


def test_settings_bool_invalid() -> None:
    with pytest.raises(ValueError):
        Settings(IS_PROD="maybe")


def test_settings_bool_native() -> None:
    settings = Settings(IS_PROD=True)
    assert settings.IS_PROD is True


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("true", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("0", False),
        ("no", False),
    ],
)
def test_client_settings_bool_parsing(value: str, expected: bool) -> None:
    settings = ClientSettings(IS_PROD=value)
    assert settings.IS_PROD is expected


def test_client_settings_bool_invalid() -> None:
    with pytest.raises(ValueError):
        ClientSettings(IS_PROD="maybe")


def test_client_settings_bool_native() -> None:
    settings = ClientSettings(IS_PROD=False)
    assert settings.IS_PROD is False
