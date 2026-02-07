from __future__ import annotations

import importlib
import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client() -> TestClient:
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["DATABASE_URL"] = f"sqlite+pysqlite:///{db_path}"
    os.environ["IS_PROD"] = "false"

    import src.interface_adapter.controller.api.app.settings as settings_module
    import src.infrastructure.db.session as session_module
    import src.infrastructure.db.models as models_module
    import src.interface_adapter.controller.api.app.deps as deps_module

    importlib.reload(settings_module)
    importlib.reload(session_module)
    importlib.reload(models_module)
    importlib.reload(deps_module)

    from src.interface_adapter.controller.api.app.main import create_app

    app = create_app()
    models_module.Base.metadata.create_all(bind=session_module.engine)
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        test_client.close()
        try:
            os.remove(db_path)
        except OSError:
            pass
