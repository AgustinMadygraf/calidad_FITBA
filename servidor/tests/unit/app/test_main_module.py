import importlib
import sys

import servidor.app.main as app_main
from infrastructure.db.unit_of_work import MySQLUnitOfWork


def test_sys_path_insertion_and_uow_factory():
    base_dir = str(app_main.BASE_DIR)
    if base_dir in sys.path:
        sys.path.remove(base_dir)
    reloaded = importlib.reload(app_main)
    assert base_dir in sys.path
    uow = reloaded.uow_factory()
    assert isinstance(uow, MySQLUnitOfWork)
