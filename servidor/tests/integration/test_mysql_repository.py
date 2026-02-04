import os
import pytest
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from infrastructure.db.unit_of_work import MySQLUnitOfWork
from application.use_cases.create_contact import CreateContact
from application.use_cases.list_contacts import ListContacts


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("DB_HOST"),
    reason="DB_HOST no configurado",
)
def test_mysql_repository_create_and_list():
    factory = MySQLConnectionFactory.from_env()
    with MySQLUnitOfWork(factory) as uow:
        create_uc = CreateContact(uow.contacts)
        create_uc.execute(full_name="Integracion", email="int@test.com")
    with MySQLUnitOfWork(factory) as uow:
        list_uc = ListContacts(uow.contacts)
        results = list_uc.execute(limit=5, offset=0)
        assert any(c.email == "int@test.com" for c in results)
