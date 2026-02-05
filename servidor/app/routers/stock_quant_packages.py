from fastapi import APIRouter, Depends, HTTPException, status
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_stock_quant_package import CreateStockQuantPackage
from application.use_cases.update_stock_quant_package import UpdateStockQuantPackage
from application.use_cases.delete_stock_quant_package import DeleteStockQuantPackage
from application.use_cases.get_stock_quant_package_by_id import GetStockQuantPackageById
from application.use_cases.list_stock_quant_packages import ListStockQuantPackages
from application.exceptions import NotFoundError, DatabaseError
from domain.exceptions import ValidationError
from servidor.app.schemas.stock_quant_package import (
    StockQuantPackageCreate,
    StockQuantPackageUpdate,
    StockQuantPackageResponse,
    StockQuantPackageListResponse,
)

router = APIRouter(prefix="/api/v1/stock-quant-packages", tags=["stock_quant_package"])


def get_uow() -> IUnitOfWork:
    from servidor.app.main import uow_factory

    return uow_factory()


def _map_dto(dto) -> StockQuantPackageResponse:
    return StockQuantPackageResponse(**dto.__dict__)


@router.post("", response_model=StockQuantPackageResponse, status_code=status.HTTP_201_CREATED)
def create_package(payload: StockQuantPackageCreate, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = CreateStockQuantPackage(uow.packages)
            dto = use_case.execute(**payload.model_dump())
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{package_id}", response_model=StockQuantPackageResponse)
def update_package(
    package_id: int, payload: StockQuantPackageUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    data = payload.model_dump(exclude_unset=True)
    try:
        with uow:
            use_case = UpdateStockQuantPackage(uow.packages)
            dto = use_case.execute(package_id=package_id, **data)
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(package_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = DeleteStockQuantPackage(uow.packages)
            use_case.execute(package_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{package_id}", response_model=StockQuantPackageResponse)
def get_package(package_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = GetStockQuantPackageById(uow.packages)
            dto = use_case.execute(package_id)
        return _map_dto(dto)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=StockQuantPackageListResponse)
def list_packages(limit: int = 10, offset: int = 0, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = ListStockQuantPackages(uow.packages)
            items = use_case.execute(limit=limit, offset=offset)
        return StockQuantPackageListResponse(
            items=[_map_dto(i) for i in items], limit=limit, offset=offset
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
