from __future__ import annotations

from types import SimpleNamespace

from src.server.app.settings import settings as server_settings
from src.server.app import deps
from src.interface_adapter.gateways.mock_xubio_api_client import MockXubioApiClient
from src.interface_adapter.gateways.real_xubio_api_client import RealXubioApiClient


def test_get_xubio_client_returns_mock(monkeypatch) -> None:
    monkeypatch.setattr(deps.settings, "IS_PROD", False)
    dummy_session = SimpleNamespace()
    client = deps.get_xubio_client(dummy_session)
    assert isinstance(client, MockXubioApiClient)


def test_get_xubio_client_returns_real(monkeypatch) -> None:
    monkeypatch.setattr(deps.settings, "IS_PROD", True)
    dummy_session = SimpleNamespace()
    client = deps.get_xubio_client(dummy_session)
    assert isinstance(client, RealXubioApiClient)
