from __future__ import annotations

import importlib


def test_import_client_main_module() -> None:
    importlib.import_module("src.interface_adapter.controller.cli.__main__")


def test_import_server_main_module() -> None:
    importlib.import_module("src.server.app.__main__")
