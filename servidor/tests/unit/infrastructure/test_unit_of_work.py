from infrastructure.db.unit_of_work import MySQLUnitOfWork


class FakeConnection:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


class FakeFactory:
    def __init__(self, conn: FakeConnection) -> None:
        self._conn = conn

    def connect(self):
        return self._conn


def test_unit_of_work_commit_and_rollback():
    conn = FakeConnection()
    uow = MySQLUnitOfWork(FakeFactory(conn))
    uow.connection = conn
    uow.__exit__(None, None, None)
    assert conn.committed is True
    assert conn.closed is True

    conn2 = FakeConnection()
    uow2 = MySQLUnitOfWork(FakeFactory(conn2))
    uow2.connection = conn2
    uow2.__exit__(Exception, Exception("x"), None)
    assert conn2.rolled_back is True
    assert conn2.closed is True


def test_unit_of_work_no_connection_exit():
    uow = MySQLUnitOfWork(FakeFactory(FakeConnection()))
    uow.connection = None
    uow.__exit__(None, None, None)
