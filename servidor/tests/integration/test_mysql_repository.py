import os
import pytest
from infrastructure.db.mysql_connection import MySQLConnectionFactory
from infrastructure.db.unit_of_work import MySQLUnitOfWork
from application.use_cases.create_res_partner import CreateResPartner
from application.use_cases.list_res_partners import ListResPartners


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("DB_HOST"),
    reason="DB_HOST no configurado",
)
def test_mysql_repository_create_and_list():
    factory = MySQLConnectionFactory.from_env()
    with MySQLUnitOfWork(factory) as uow:
        create_uc = CreateResPartner(uow.partners)
        create_uc.execute(name="Integracion", email="int@test.com")
    with MySQLUnitOfWork(factory) as uow:
        list_uc = ListResPartners(uow.partners)
        results = list_uc.execute(limit=5, offset=0)
        assert any(c.email == "int@test.com" for c in results)
