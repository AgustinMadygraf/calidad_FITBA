from __future__ import annotations

import importlib
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    temp_db = tempfile.NamedTemporaryFile(suffix=".db")
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{temp_db.name}"
    os.environ["IS_PROD"] = "false"

    import src.server.app.settings as settings_module
    import src.server.infrastructure.db.session as session_module
    import src.server.infrastructure.db.models as models_module
    import src.server.app.deps as deps_module

    importlib.reload(settings_module)
    importlib.reload(session_module)
    importlib.reload(models_module)
    importlib.reload(deps_module)

    from src.server.app.main import create_app

    app = create_app()
    models_module.Base.metadata.create_all(bind=session_module.engine)
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        temp_db.close()
