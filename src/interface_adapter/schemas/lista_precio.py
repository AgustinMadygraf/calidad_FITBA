from pydantic import BaseModel, ConfigDict


class ListaPrecioSimpleItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    ID: int | None = None
    nombre: str | None = None
    codigo: str | None = None
    id: int | None = None


class ListaPrecioItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    listaPrecioID: int | None = None
    producto: ListaPrecioSimpleItem | None = None
    precio: float | int | None = None
    codigo: str | None = None
    referencia: float | int | None = None


class ListaPrecioDetailResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    listaPrecioID: int | None = None
    activo: bool | None = None
    nombre: str | None = None
    descripcion: str | None = None
    esDefault: bool | None = None
    moneda: ListaPrecioSimpleItem | None = None
    tipo: int | None = None
    iva: int | None = None
    listaReferencia: ListaPrecioSimpleItem | None = None
    listaPrecioItem: list[ListaPrecioItem] | None = None
    ocultarSinPrecio: bool | None = None
