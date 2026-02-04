import pytest
from infrastructure.repositories.in_memory_contact_repository import InMemoryContactRepository
from application.use_cases.create_contact import CreateContact
from application.use_cases.update_contact import UpdateContact
from application.use_cases.delete_contact import DeleteContact
from application.use_cases.get_contact_by_id import GetContactById
from application.use_cases.search_contacts import SearchContacts
from application.use_cases.list_contacts import ListContacts
from application.exceptions import NotFoundError


def test_create_and_get_contact():
    repo = InMemoryContactRepository()
    create_uc = CreateContact(repo)
    dto = create_uc.execute(full_name="Ana", email="ana@example.com")
    get_uc = GetContactById(repo)
    loaded = get_uc.execute(dto.id)
    assert loaded.email == "ana@example.com"


def test_update_contact():
    repo = InMemoryContactRepository()
    create_uc = CreateContact(repo)
    dto = create_uc.execute(full_name="Ana")
    update_uc = UpdateContact(repo)
    updated = update_uc.execute(dto.id, full_name="Ana Maria", phone="123")
    assert updated.full_name == "Ana Maria"


def test_delete_contact():
    repo = InMemoryContactRepository()
    create_uc = CreateContact(repo)
    dto = create_uc.execute(full_name="Ana")
    delete_uc = DeleteContact(repo)
    delete_uc.execute(dto.id)
    get_uc = GetContactById(repo)
    with pytest.raises(NotFoundError):
        get_uc.execute(dto.id)


def test_search_and_list():
    repo = InMemoryContactRepository()
    create_uc = CreateContact(repo)
    create_uc.execute(full_name="Juan", email="juan@test.com")
    create_uc.execute(full_name="Maria", phone="555")

    search_uc = SearchContacts(repo)
    results = search_uc.execute("juan", limit=10, offset=0)
    assert len(results) == 1

    list_uc = ListContacts(repo)
    results = list_uc.execute(limit=10, offset=0)
    assert len(results) == 2
