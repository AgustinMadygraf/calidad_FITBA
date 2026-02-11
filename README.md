# FITBA Xubio-like (MVP)

Monorepo Python con dos componentes:
- FastAPI (API local Xubio-like).
- CLI estilo terminal AS400 (stub).

## Arquitectura (Clean Architecture)
- `src/entities/`: entidades y modelos de dominio.
- `src/use_cases/`: casos de uso.
- `src/interface_adapter/`: controllers, presenters y esquemas.
- `src/infrastructure/`: gateways HTTPX, FastAPI y memoria.
- `src/shared/`: helpers comunes (config/logger).

## Estado actual
- Cliente: CRUD.
- Remito venta: CRUD con validaciones de cliente, producto, deposito y lista de precio.
- Producto venta y compra: GET list/get.
- Depositos: GET list/get.
- Lista de precio: GET list/get.
- Token inspect local: `GET /token/inspect`.

## API local (FastAPI)
- `GET /health`
- `GET /token/inspect`
- `GET /API/1.1/clienteBean`
- `POST /API/1.1/clienteBean`
- `GET /API/1.1/clienteBean/{id}`
- `PUT /API/1.1/clienteBean/{id}`
- `DELETE /API/1.1/clienteBean/{id}`
- `GET /API/1.1/remitoVentaBean`
- `POST /API/1.1/remitoVentaBean`
- `GET /API/1.1/remitoVentaBean/{id}`
- `PUT /API/1.1/remitoVentaBean/{id}`
- `DELETE /API/1.1/remitoVentaBean/{id}`
- `GET /API/1.1/productoVentaBean`
- `GET /API/1.1/productoVentaBean/{id}`
- `GET /API/1.1/productoCompraBean`
- `GET /API/1.1/productoCompraBean/{id}`
- `GET /API/1.1/depositos`
- `GET /API/1.1/depositos/{id}`
- `GET /API/1.1/listaPrecioBean`
- `GET /API/1.1/listaPrecioBean/{id}`
- `GET /debug/clienteBean` (solo en `IS_PROD=false`)

## Resumen Xubio API
Xubio expone una API REST para integrar emision de comprobantes electronicos y
otras operaciones sin reinventar funcionalidad existente. La API usa OAuth2 con
`client_credentials` y se autentica con `Client-ID` y `Secret-ID` para obtener
un `access_token`.

Referencia rapida en `docs/xubio.md`.

Documentacion adicional:
- `docs/api_local.md`
- `docs/arquitectura.md`

## Requisitos
- Python 3.11+

## Instalacion

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno

```
IS_PROD=false
XUBIO_CLIENT_ID=...
XUBIO_SECRET_ID=...
XUBIO_TOKEN_ENDPOINT=https://xubio.com/API/1.1/TokenEndpoint
PORT=8000
```

Nota: `IS_PROD` acepta `true/false`, `1/0`, `yes/no`.

Modo en servidor:
- `IS_PROD=false`: usa gateways in-memory para clientes, remitos, productos,
  depositos y listas de precio.
- `IS_PROD=true`: usa gateways HTTPX y requiere OAuth2 (token real de Xubio).

## Ejecutar servidor

```bash
uvicorn src.infrastructure.fastapi.api:app --reload --host 127.0.0.1 --port 8000
```

```bash
python -m src.infrastructure.fastapi.api
```

```bash
python run.py
```

Override por argumento (prioridad sobre `.env`):

```bash
python run.py --IS_PROD=true
python run.py --IS_PROD=false
```

## Tests

```bash
pytest -q
```

## Notas
- En modo real, la baja de recursos impacta datos reales en Xubio.
- En modo real, el cliente requiere doble confirmacion para BAJA.
