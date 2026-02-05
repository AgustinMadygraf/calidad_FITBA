from __future__ import annotations

import importlib
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    os.environ["XUBIO_MODE"] = "mock"

    import server.app.settings as settings_module
    import server.infrastructure.db.session as session_module
    import server.infrastructure.db.models as models_module
    import server.app.deps as deps_module

    importlib.reload(settings_module)
    importlib.reload(session_module)
    importlib.reload(models_module)
    importlib.reload(deps_module)

    from server.app.main import create_app

    app = create_app()
    models_module.Base.metadata.create_all(bind=session_module.engine)
    return TestClient(app)
