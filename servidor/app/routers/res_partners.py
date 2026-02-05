from fastapi import APIRouter, Depends, HTTPException, status
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_res_partner import CreateResPartner
from application.use_cases.update_res_partner import UpdateResPartner
from application.use_cases.delete_res_partner import DeleteResPartner
from application.use_cases.get_res_partner_by_id import GetResPartnerById
from application.use_cases.list_res_partners import ListResPartners
from application.exceptions import NotFoundError, DatabaseError
from domain.exceptions import ValidationError
from servidor.app.schemas.res_partner import (
    ResPartnerCreate,
    ResPartnerUpdate,
    ResPartnerResponse,
    ResPartnerListResponse,
)

router = APIRouter(prefix="/api/v1/res-partners", tags=["res_partner"])


def get_uow() -> IUnitOfWork:
    from servidor.app.main import uow_factory

    return uow_factory()


def _map_dto(dto) -> ResPartnerResponse:
    return ResPartnerResponse(**dto.__dict__)


@router.post("", response_model=ResPartnerResponse, status_code=status.HTTP_201_CREATED)
def create_partner(payload: ResPartnerCreate, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = CreateResPartner(uow.partners)
            dto = use_case.execute(**payload.model_dump())
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{partner_id}", response_model=ResPartnerResponse)
def update_partner(
    partner_id: int, payload: ResPartnerUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    data = payload.model_dump(exclude_unset=True)
    try:
        with uow:
            use_case = UpdateResPartner(uow.partners)
            dto = use_case.execute(partner_id=partner_id, **data)
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{partner_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_partner(partner_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = DeleteResPartner(uow.partners)
            use_case.execute(partner_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{partner_id}", response_model=ResPartnerResponse)
def get_partner(partner_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = GetResPartnerById(uow.partners)
            dto = use_case.execute(partner_id)
        return _map_dto(dto)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=ResPartnerListResponse)
def list_partners(limit: int = 10, offset: int = 0, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = ListResPartners(uow.partners)
            items = use_case.execute(limit=limit, offset=offset)
        return ResPartnerListResponse(
            items=[_map_dto(i) for i in items], limit=limit, offset=offset
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
