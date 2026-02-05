from infrastructure.repositories.in_memory_res_partner_repository import InMemoryResPartnerRepository
from application.use_cases.create_res_partner import CreateResPartner
from application.use_cases.update_res_partner import UpdateResPartner
from application.use_cases.delete_res_partner import DeleteResPartner
from application.use_cases.get_res_partner_by_id import GetResPartnerById
from application.use_cases.list_res_partners import ListResPartners
from application.exceptions import NotFoundError


def test_create_and_get_partner():
    repo = InMemoryResPartnerRepository()
    create_uc = CreateResPartner(repo)
    get_uc = GetResPartnerById(repo)

    created = create_uc.execute(name="Cliente A", email="a@b.com")
    fetched = get_uc.execute(created.id)
    assert fetched.name == "Cliente A"


def test_update_partner():
    repo = InMemoryResPartnerRepository()
    create_uc = CreateResPartner(repo)
    update_uc = UpdateResPartner(repo)

    created = create_uc.execute(name="Cliente A")
    updated = update_uc.execute(created.id, name="Cliente B")
    assert updated.name == "Cliente B"


def test_delete_partner():
    repo = InMemoryResPartnerRepository()
    create_uc = CreateResPartner(repo)
    delete_uc = DeleteResPartner(repo)
    list_uc = ListResPartners(repo)

    created = create_uc.execute(name="Cliente A")
    delete_uc.execute(created.id)
    items = list_uc.execute(limit=10, offset=0)
    assert items == []


def test_get_partner_not_found():
    repo = InMemoryResPartnerRepository()
    get_uc = GetResPartnerById(repo)
    try:
        get_uc.execute(999)
        assert False, "Expected NotFoundError"
    except NotFoundError:
        assert True
