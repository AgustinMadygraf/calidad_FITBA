import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("IS_PROD", "false")


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
