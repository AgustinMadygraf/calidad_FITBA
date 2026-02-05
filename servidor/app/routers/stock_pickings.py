from fastapi import APIRouter, Depends, HTTPException, status
from application.ports.unit_of_work import IUnitOfWork
from application.use_cases.create_stock_picking import CreateStockPicking
from application.use_cases.update_stock_picking import UpdateStockPicking
from application.use_cases.delete_stock_picking import DeleteStockPicking
from application.use_cases.get_stock_picking_by_id import GetStockPickingById
from application.use_cases.list_stock_pickings import ListStockPickings
from application.exceptions import NotFoundError, DatabaseError
from domain.exceptions import ValidationError
from servidor.app.schemas.stock_picking import (
    StockPickingCreate,
    StockPickingUpdate,
    StockPickingResponse,
    StockPickingListResponse,
)

router = APIRouter(prefix="/api/v1/stock-pickings", tags=["stock_picking"])


def get_uow() -> IUnitOfWork:
    from servidor.app.main import uow_factory

    return uow_factory()


def _map_dto(dto) -> StockPickingResponse:
    return StockPickingResponse(**dto.__dict__)


@router.post("", response_model=StockPickingResponse, status_code=status.HTTP_201_CREATED)
def create_picking(payload: StockPickingCreate, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = CreateStockPicking(uow.pickings)
            dto = use_case.execute(**payload.model_dump())
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{picking_id}", response_model=StockPickingResponse)
def update_picking(
    picking_id: int, payload: StockPickingUpdate, uow: IUnitOfWork = Depends(get_uow)
):
    data = payload.model_dump(exclude_unset=True)
    try:
        with uow:
            use_case = UpdateStockPicking(uow.pickings)
            dto = use_case.execute(picking_id=picking_id, **data)
        return _map_dto(dto)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{picking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_picking(picking_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = DeleteStockPicking(uow.pickings)
            use_case.execute(picking_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{picking_id}", response_model=StockPickingResponse)
def get_picking(picking_id: int, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = GetStockPickingById(uow.pickings)
            dto = use_case.execute(picking_id)
        return _map_dto(dto)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("", response_model=StockPickingListResponse)
def list_pickings(limit: int = 10, offset: int = 0, uow: IUnitOfWork = Depends(get_uow)):
    try:
        with uow:
            use_case = ListStockPickings(uow.pickings)
            items = use_case.execute(limit=limit, offset=offset)
        return StockPickingListResponse(
            items=[_map_dto(i) for i in items], limit=limit, offset=offset
        )
    except DatabaseError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
