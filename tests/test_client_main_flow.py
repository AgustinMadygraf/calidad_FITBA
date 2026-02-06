from __future__ import annotations

import pytest

import src.client.app.main as main_module
from src.client.app.product_gateway import LocalFastApiProductGateway, XubioDirectProductGateway


class _FakeGateway:
    title = "FAKE"
    show_sync_pull = True
    back_option = "7"

    def __init__(self) -> None:
        self.actions: list[str] = []

    def render_menu(self, session_id: str) -> str:
        _ = session_id
        return "1) Alta\n5) Listar\n6) Sync\n7) Volver"

    def create(self, *, session_id: str, external_id: str | None, name: str, sku: str | None, price: float | None) -> str:
        _ = (session_id, external_id, name, sku, price)
        self.actions.append("create")
        return "CREATED"

    def update(self, *, session_id: str, external_id: str, name: str | None, sku: str | None, price: float | None) -> str:
        _ = (session_id, external_id, name, sku, price)
        self.actions.append("update")
        return "UPDATED"

    def delete(self, *, session_id: str, external_id: str) -> str:
        _ = (session_id, external_id)
        self.actions.append("delete")
        return "DELETED"

    def get(self, *, session_id: str, external_id: str) -> str:
        _ = (session_id, external_id)
        self.actions.append("get")
        return "GET"

    def list(self, *, session_id: str) -> str:
        _ = session_id
        self.actions.append("list")
        return "Productos:\nID | Nombre\n- p-1 | A"

    def sync_pull(self, *, session_id: str) -> str:
        _ = session_id
        self.actions.append("sync")
        return "Sync pull OK"

    def on_back(self, session_id: str) -> None:
        _ = session_id
        self.actions.append("back")


def test_product_menu_create_list_sync_and_back(monkeypatch) -> None:
    gateway = _FakeGateway()
    inputs = iter(
        [
            "1",  # create
            "",  # id
            "Nombre",  # name
            "",  # sku
            "",  # price
            "S",  # continue without price
            "",  # pause
            "5",  # list
            "",  # pause from paginated screen
            "6",  # sync
            "",  # pause
            "7",  # back
        ]
    )

    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_clear", lambda: None)
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_render_paginated_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)
    monkeypatch.setattr(main_module, "_is_prod_enabled", lambda: False)

    main_module._product_menu("s", gateway)
    assert gateway.actions == ["create", "list", "sync", "back"]


def test_product_menu_update_delete_get_and_invalid(monkeypatch) -> None:
    gateway = _FakeGateway()
    inputs = iter(
        [
            "2",  # update
            "p-1",  # id
            "",  # name
            "SKU",  # sku
            "12",  # price
            "",  # pause
            "3",  # delete
            "p-1",  # id
            "SI",  # confirm 1
            "SI",  # confirm 2
            "",  # pause
            "4",  # get
            "p-1",  # id
            "",  # pause
            "9",  # invalid
            "",  # pause
            "7",  # back
        ]
    )

    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_clear", lambda: None)
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)
    monkeypatch.setattr(main_module, "_is_prod_enabled", lambda: True)

    main_module._product_menu("s", gateway)
    assert gateway.actions == ["update", "delete", "get", "back"]


def test_product_menu_quit(monkeypatch) -> None:
    gateway = _FakeGateway()
    inputs = iter(["q"])

    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_clear", lambda: None)
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)

    with pytest.raises(SystemExit):
        main_module._product_menu("s", gateway)


def test_render_paginated_screen_multi_page(monkeypatch) -> None:
    inputs = iter(["q"])
    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_term_height", lambda min_height=20: 10)
    monkeypatch.setattr(main_module, "_clear", lambda: None)

    body = "\n".join([f"line {i}" for i in range(20)])
    main_module._render_paginated_screen("TITLE", body)


def test_field_prompt_required_missing(monkeypatch) -> None:
    inputs = iter([""])
    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)

    assert main_module._field_prompt("Nombre", required=True) is None


def test_read_price_invalid(monkeypatch) -> None:
    inputs = iter(["abc", ""])
    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)

    assert main_module._read_price() is None


def test_double_confirm(monkeypatch) -> None:
    inputs = iter(["SI", "SI"])
    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    assert main_module._double_confirm() is True


def test_build_gateway(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_IS_PROD_OVERRIDE", False)
    gateway = main_module._build_product_gateway()
    assert isinstance(gateway, LocalFastApiProductGateway)

    monkeypatch.setattr(main_module, "_IS_PROD_OVERRIDE", True)
    monkeypatch.setattr(main_module.settings, "xubio_client_id", None)
    monkeypatch.setattr(main_module.settings, "xubio_secret_id", None)
    with pytest.raises(ValueError):
        main_module._build_product_gateway()


def test_run_exits(monkeypatch) -> None:
    inputs = iter(["q"])
    monkeypatch.setattr(main_module, "_prompt", lambda _: next(inputs))
    monkeypatch.setattr(main_module, "_clear", lambda: None)
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_build_product_gateway", lambda: _FakeGateway())

    with pytest.raises(SystemExit):
        main_module.run(is_prod="false")


def test_stub_screen(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)
    main_module._stub_screen("s", "client")


def test_run_action_error(monkeypatch) -> None:
    monkeypatch.setattr(main_module, "_render_screen", lambda *args, **kwargs: None)
    monkeypatch.setattr(main_module, "_pause", lambda: None)

    def _boom():
        raise RuntimeError("fail")

    assert main_module._run_action("x", _boom) is None
