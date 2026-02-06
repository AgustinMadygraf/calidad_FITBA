from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.server.app.settings import settings as server_settings
from src.server.infrastructure.db.models import Base
from src.server.infrastructure.repositories.integration_record_repository import (
    IntegrationRecordRepository,
)
from src.server.infrastructure.clients.mock_xubio_api_client import MockXubioApiClient
from src.server.interfaces.terminal import execute_command
from src.server.interfaces.api import routes
from src.shared.schemas import ProductCreate, ProductUpdate


def _make_repo() -> IntegrationRecordRepository:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    return IntegrationRecordRepository(session)


def test_execute_command_menu_and_product_flow(monkeypatch) -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    session_id, screen, actions = execute_command(
        session_id="s",
        command="MENU",
        args={},
        client=client,
        repository=repo,
    )
    assert session_id == "s"
    assert "TERMINAL FITBA/XUBIO" in screen
    assert "ENTER product" in actions[0]

    session_id, screen, _ = execute_command(
        session_id="s",
        command="CREATE product",
        args={"external_id": "p-1", "name": "Producto A"},
        client=client,
        repository=repo,
    )
    assert "Producto creado" in screen

    session_id, screen, _ = execute_command(
        session_id="s",
        command="GET product",
        args={"external_id": "p-1"},
        client=client,
        repository=repo,
    )
    assert "Producto:" in screen

    session_id, screen, _ = execute_command(
        session_id="s",
        command="LIST product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Productos:" in screen

    session_id, screen, _ = execute_command(
        session_id="s",
        command="SYNC_PULL product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Sync pull OK" in screen


def test_execute_command_delete_blocked_in_prod(monkeypatch) -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)
    monkeypatch.setattr(server_settings, "IS_PROD", True)
    monkeypatch.setattr(server_settings, "disable_delete_in_real", True)

    _, screen, _ = execute_command(
        session_id="s",
        command="DELETE product",
        args={"external_id": "p-1"},
        client=client,
        repository=repo,
    )
    assert "Baja deshabilitada" in screen


def test_execute_command_errors_and_stub() -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    _, screen, _ = execute_command(
        session_id="s",
        command="ENTER client",
        args={},
        client=client,
        repository=repo,
    )
    assert "No implementado" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="UPDATE product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Falta external_id" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="DELETE product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Falta external_id" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="GET product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Falta external_id" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="UNKNOWN",
        args={},
        client=client,
        repository=repo,
    )
    assert "Comando desconocido" in screen


def test_execute_command_empty_and_back_and_list_empty() -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    _, screen, actions = execute_command(
        session_id="s",
        command="   ",
        args={},
        client=client,
        repository=repo,
    )
    assert "TERMINAL FITBA/XUBIO" in screen
    assert actions == ["MENU"]

    _, screen, actions = execute_command(
        session_id="s",
        command="BACK",
        args={},
        client=client,
        repository=repo,
    )
    assert "TERMINAL FITBA/XUBIO" in screen
    assert actions == ["MENU"]

    _, screen, _ = execute_command(
        session_id="s",
        command="LIST product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Sin productos" in screen


def test_execute_command_update_delete_get_success() -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    _, _, _ = execute_command(
        session_id="s",
        command="CREATE product",
        args={"external_id": "p-1", "name": "Producto A"},
        client=client,
        repository=repo,
    )

    _, screen, _ = execute_command(
        session_id="s",
        command="UPDATE product",
        args={"external_id": "p-1", "name": "Producto B"},
        client=client,
        repository=repo,
    )
    assert "Producto actualizado" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="GET",
        args={"entity_type": "product", "external_id": "p-1"},
        client=client,
        repository=repo,
    )
    assert "SKU: -" in screen
    assert "Precio: -" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="DELETE",
        args={"entity_type": "product", "external_id": "p-1"},
        client=client,
        repository=repo,
    )
    assert "Producto eliminado" in screen


def test_render_helpers_and_enter_paths(monkeypatch) -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    from src.server.interfaces import terminal as terminal_module

    assert "TERMINAL FITBA/XUBIO" in terminal_module._render_main_menu()
    assert "PRODUCT" in terminal_module._render_entity_menu("product")
    assert "No implementado" in terminal_module._render_stub()

    _, screen, _ = execute_command(
        session_id="s",
        command="ENTER product",
        args={},
        client=client,
        repository=repo,
    )
    assert "PRODUCT" in screen

    _, screen, _ = execute_command(
        session_id="s",
        command="ENTER",
        args={"entity_type": "client"},
        client=client,
        repository=repo,
    )
    assert "No implementado" in screen


def test_execute_command_sync_pull_error(monkeypatch) -> None:
    repo = _make_repo()
    client = MockXubioApiClient(repo)

    class _FakeSync:
        def __init__(self, *args, **kwargs):
            _ = (args, kwargs)

        def execute(self, is_mock: bool):
            _ = is_mock
            return {"status": "error", "detail": "fallo"}

    import src.server.interfaces.terminal as terminal_module

    monkeypatch.setattr(terminal_module, "SyncPullProduct", _FakeSync)

    _, screen, _ = execute_command(
        session_id="s",
        command="SYNC_PULL product",
        args={},
        client=client,
        repository=repo,
    )
    assert "Sync pull ERROR" in screen


def test_routes_mapping_helpers() -> None:
    payload = routes.XubioProductPayload(
        productoid="p-1",
        nombre="Producto",
        codigo="SKU",
        precioVenta=1.5,
    )
    dto = routes._to_product_create(payload)
    assert dto == ProductCreate(external_id="p-1", name="Producto", sku="SKU", price=1.5)

    dto_update = routes._to_product_update(payload)
    assert dto_update == ProductUpdate(name="Producto", sku="SKU", price=1.5)

    mapped = routes._map_to_xubio(dto)
    assert mapped["productoid"] == "p-1"


def test_routes_missing_name_raises() -> None:
    payload = routes.XubioProductPayload(productoid="p-1")
    try:
        routes._to_product_create(payload)
    except Exception as exc:
        assert "Falta nombre" in str(exc)
    else:
        raise AssertionError("Expected exception")
