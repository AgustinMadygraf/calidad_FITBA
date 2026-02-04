import pytest

httpx = pytest.importorskip("httpx")

from infrastructure.repositories.in_memory_contact_repository import InMemoryContactRepository
from application.ports.unit_of_work import IUnitOfWork
from servidor.app.main import create_app


class FakeUoW(IUnitOfWork):
    def __init__(self) -> None:
        self.contacts = InMemoryContactRepository()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        pass


def test_create_and_list_api(monkeypatch):
    def _uow_factory():
        return FakeUoW()

    monkeypatch.setattr("servidor.app.main.uow_factory", _uow_factory)
    app = create_app()

    transport = httpx.ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://test") as client:
        r = client.post(
            "/api/v1/contacts",
            json={"full_name": "Ana", "email": "ana@example.com"},
        )
        assert r.status_code == 201
        data = r.json()
        assert data["email"] == "ana@example.com"

        r = client.get("/api/v1/contacts")
        assert r.status_code == 200
        items = r.json()["items"]
        assert len(items) == 1
