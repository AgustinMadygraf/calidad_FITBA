from fastapi import APIRouter, Depends, HTTPException, status
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_stock_package_type import CreateStockPackageType
from application.use_cases.update_stock_package_type import UpdateStockPackageType
from application.use_cases.delete_stock_package_type import DeleteStockPackageType
from application.use_cases.get_stock_package_type_by_id import GetStockPackageTypeById
from application.use_cases.list_stock_package_types import ListStockPackageTypes
from application.exceptions import NotFoundError, DatabaseError
from domain.exceptions import ValidationError
from servidor.app.schemas.stock_package_type import (
    StockPackageTypeCreate,
    StockPackageTypeUpdate,
    StockPackageTypeResponse,
    StockPackageTypeListResponse,
)

router = APIRouter(prefix="/api/v1/stock-package-types", tags=["stock_package_type"])


def get_uow() -> IUnitOfWork:
    from servidor.app.main import uow_factory

    return uow_factory()


def _map_dto(dto) -> StockPackageTypeResponse:
    return StockPackageTypeResponse(**dto.__dict__)


@router.post("", response_model=StockPackageTypeResponse, status_code=status.HTTP_201_CREATED)
def create_package_type(payload: StockPackageTypeCreate, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = CreateStockPackageType(uow.package_types)
            dto = use_case.execute(**payload.model_dump())
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{package_type_id}", response_model=StockPackageTypeResponse)
def update_package_type(
    package_type_id: int, payload: StockPackageTypeUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    data = payload.model_dump(exclude_unset=True)
    try:
        with uow:
            use_case = UpdateStockPackageType(uow.package_types)
            dto = use_case.execute(package_type_id=package_type_id, **data)
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{package_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package_type(package_type_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = DeleteStockPackageType(uow.package_types)
            use_case.execute(package_type_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{package_type_id}", response_model=StockPackageTypeResponse)
def get_package_type(package_type_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = GetStockPackageTypeById(uow.package_types)
            dto = use_case.execute(package_type_id)
        return _map_dto(dto)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=StockPackageTypeListResponse)
def list_package_types(limit: int = 10, offset: int = 0, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = ListStockPackageTypes(uow.package_types)
            items = use_case.execute(limit=limit, offset=offset)
        return StockPackageTypeListResponse(
            items=[_map_dto(i) for i in items], limit=limit, offset=offset
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
