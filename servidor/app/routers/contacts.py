from fastapi import APIRouter, Depends, HTTPException, status
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_contact import CreateContact
from application.use_cases.update_contact import UpdateContact
from application.use_cases.delete_contact import DeleteContact
from application.use_cases.get_contact_by_id import GetContactById
from application.use_cases.list_contacts import ListContacts
from application.use_cases.search_contacts import SearchContacts
from application.exceptions import NotFoundError, DatabaseError
from domain.exceptions import ValidationError, DuplicateEmailError
from servidor.app.schemas.contacts import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
)

router = APIRouter(prefix="/api/v1/contacts", tags=["contacts"])


def get_uow() -> IUnitOfWork:
    from servidor.app.main import uow_factory

    return uow_factory()


def _map_dto(dto) -> ContactResponse:
    return ContactResponse(**dto.__dict__)


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = CreateContact(uow.contacts)
            dto = use_case.execute(**payload.model_dump())
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int, payload: ContactUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    data = payload.model_dump(exclude_unset=True)

    def normalize_optional(value: str | None) -> str | None:
        if value is None:
            return ""
        return value

    if "email" in data:
        data["email"] = normalize_optional(data["email"])
    if "phone" in data:
        data["phone"] = normalize_optional(data["phone"])
    if "company" in data and data["company"] is None:
        data["company"] = ""
    if "notes" in data and data["notes"] is None:
        data["notes"] = ""

    try:
        with uow:
            use_case = UpdateContact(uow.contacts)
            dto = use_case.execute(contact_id=contact_id, **data)
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DuplicateEmailError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = DeleteContact(uow.contacts)
            use_case.execute(contact_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = GetContactById(uow.contacts)
            dto = use_case.execute(contact_id)
        return _map_dto(dto)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=ContactListResponse)
def list_contacts(
    q: str | None = None, limit: int = 10, offset: int = 0, uow: IUnitOfWork = Depends(get_uow)
):
    try:
        with uow:
            if q:
                use_case = SearchContacts(uow.contacts)
                items = use_case.execute(query=q, limit=limit, offset=offset)
            else:
                use_case = ListContacts(uow.contacts)
                items = use_case.execute(limit=limit, offset=offset)
        return ContactListResponse(
            items=[_map_dto(i) for i in items], limit=limit, offset=offset
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
