import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("IS_PROD", "false")


def pytest_configure(config):
    config.addinivalue_line("markers", "unit: Unit tests (isolated logic).")
    config.addinivalue_line(
        "markers", "integration: Integration tests (gateway/infra boundaries)."
    )
    config.addinivalue_line(
        "markers", "api_http: HTTP-level API tests (FastAPI TestClient)."
    )
    config.addinivalue_line("markers", "contract: Contract tests vs swagger.")


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
