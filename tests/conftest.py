import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests (isolated logic).")
    config.addinivalue_line(
        "markers", "integration: Integration tests (gateway/infra boundaries)."
    )
    config.addinivalue_line(
        "markers", "api_http: HTTP-level API tests (FastAPI TestClient)."
    )
    config.addinivalue_line("markers", "contract: Contract tests vs swagger.")
    config.addinivalue_line("markers", "legacy: Tests obsoletos fuera de alcance actual.")


LEGACY_TEST_FILES = {
    "test_api_error_branches.py",
    "test_api_success_branches.py",
    "test_cliente_api.py",
    "test_cliente_gateway_xubio.py",
    "test_fastapi_deps_unit.py",
    "test_lista_precio_api.py",
    "test_lista_precio_gateway_xubio.py",
    "test_observability_api.py",
    "test_payload_validation_api.py",
    "test_remito_api.py",
    "test_remito_gateway_xubio.py",
    "test_runtime_mode_policy.py",
    "test_runtime_policy_unit.py",
    "test_shared_config.py",
    "test_use_case_terminal_cli.py",
    "test_xubio_cache_helpers.py",
    "test_xubio_crud_helpers.py",
}


def _classify_marker(path: Path) -> str:
    name = path.name
    if "contract" in name:
        return "contract"
    if name.startswith("test_api_") or name.endswith("_api.py"):
        return "api_http"
    if "gateway_xubio" in name or "gateway_httpx" in name:
        return "integration"
    return "unit"


def pytest_collection_modifyitems(config, items):
    for item in items:
        file_name = Path(str(item.fspath)).name
        if file_name in LEGACY_TEST_FILES:
            item.add_marker(pytest.mark.legacy)
            item.add_marker(
                pytest.mark.skip(
                    reason="Fuera de alcance read-only actual (legacy pre-refactor)."
                )
            )
            continue
        marker = _classify_marker(Path(str(item.fspath)))
        item.add_marker(getattr(pytest.mark, marker))


@pytest.fixture
def app_fixture():
    from src.infrastructure.fastapi.app import create_app
    from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway

    app = create_app()
    app.cliente_gateway = InMemoryClienteGateway()
    app.cliente_gateway_fixture = app.cliente_gateway
    return app


@pytest.fixture
def cliente_gateway():
    from src.infrastructure.memory.cliente_gateway_memory import InMemoryClienteGateway

    return InMemoryClienteGateway()


@pytest.fixture(autouse=True)
def reset_gateway_provider():
    from src.infrastructure.fastapi.gateway_provider import gateway_provider

    gateway_provider.reset()
    yield
    gateway_provider.reset()
