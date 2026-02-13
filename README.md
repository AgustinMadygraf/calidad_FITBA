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
- Moneda: GET list/get.
- Comprobante venta: GET list/get.
- Token inspect local: `GET /token/inspect`.

## Dependencias de "Lista de Precio" (en este proyecto)
- `listaPrecioBean` se usa como catalogo de referencia (CRUD local alineado a Swagger).
- `Cliente` depende de `Lista de Precio` de forma opcional por `listaPrecioVenta`.
- `RemitoVenta` depende de `Lista de Precio` de forma opcional por `listaPrecioId`.
- `Lista de Precio` no depende de `Cliente`, `RemitoVenta`, `Producto` ni `Deposito`.

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
- `PUT /API/1.1/remitoVentaBean`
- `GET /API/1.1/remitoVentaBean/{id}`
- `PUT /API/1.1/remitoVentaBean/{id}`
- `DELETE /API/1.1/remitoVentaBean/{id}`
- `GET /API/1.1/ProductoVentaBean`
- `POST /API/1.1/ProductoVentaBean`
- `GET /API/1.1/ProductoVentaBean/{id}`
- `PUT /API/1.1/ProductoVentaBean/{id}`
- `PATCH /API/1.1/ProductoVentaBean/{id}`
- `DELETE /API/1.1/ProductoVentaBean/{id}`
- `GET /API/1.1/ProductoCompraBean`
- `GET /API/1.1/ProductoCompraBean/{id}`
- `GET /API/1.1/depositos`
- `GET /API/1.1/depositos/{id}`
- `GET /API/1.1/listaPrecioBean`
- `POST /API/1.1/listaPrecioBean`
- `GET /API/1.1/listaPrecioBean/{id}`
- `PUT /API/1.1/listaPrecioBean/{id}`
- `PATCH /API/1.1/listaPrecioBean/{id}`
- `DELETE /API/1.1/listaPrecioBean/{id}`
- `GET /API/1.1/monedaBean`
- `GET /API/1.1/monedaBean/{id}`
- `GET /API/1.1/vendedorBean`
- `GET /API/1.1/vendedorBean/{id}`
- `GET /API/1.1/comprobanteVentaBean`
- `GET /API/1.1/comprobanteVentaBean/{id}`
- `POST /observability/events`
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
- Python 3.10+

## Instalacion

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno

```
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/xubio_db
XUBIO_CLIENT_ID=...
XUBIO_SECRET_ID=...
```

El resto de configuraciones vive en `src/shared/config.py`:
- modo (`APP_IS_PROD`)
- host/port (`APP_HOST`, `APP_PORT`)
- endpoint token (`XUBIO_TOKEN_ENDPOINT`)
- cache-aside (`XUBIO_GET_CACHE_ENABLED` y `XUBIO_LIST_TTL_SECONDS`)
- editar el bloque `TEAM-EDITABLE CONFIGURATION`

Nota: `IS_PROD` puede sobreescribirse por argumento al ejecutar `run.py`.

Modo en servidor:
- `IS_PROD=false`: usa gateways HTTPX Xubio en modo solo lectura:
  - `GET` con cache-aside (cache hit -> responde; miss -> consulta Xubio y cachea).
  - `POST/PUT/PATCH/DELETE` bloqueados con `403`.
- `IS_PROD=true`: usa gateways HTTPX Xubio sin cache de lectura:
  - cada `GET` consulta directo a Xubio.
  - `POST/PUT/PATCH/DELETE` habilitados.

Cache de lectura Xubio (TTL en segundos, aplica cuando `IS_PROD=false`):
- Cliente, Remito, Producto, Deposito, Moneda, Lista de Precio, Vendedor.
- Comprobante Venta.
- Categoria Fiscal e Identificacion Tributaria.
- Los endpoint `GET .../{id}` de catalogos livianos (`monedaBean`,
  `categoriaFiscal`, `identificacionTributaria`, `depositos`) resuelven desde
  `GET list` + busqueda por ID para reducir llamadas.
- `GET /API/1.1/listaPrecioBean/{id}` consulta primero el endpoint detalle
  oficial y cae al listado solo ante respuestas `5xx`.
- `GET /API/1.1/comprobanteVentaBean/{id}` consulta primero el detalle oficial
  y cae al listado solo ante respuestas `5xx`.
- `XUBIO_GET_CACHE_ENABLED` permite override explicito de cache de lectura.

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

Override por argumento:

```bash
python run.py --IS_PROD=true
python run.py --IS_PROD=false
```

## Ejecutar CLI AS400 (MVP)

```bash
python run_cli.py --base-url http://localhost:8000
```

Flags utiles:
- `--base-url`: URL base de la API local (default `http://localhost:8000`).
- `--timeout`: timeout HTTP en segundos.
- `--no-banner`: inicia sin imprimir el menu.

Comandos disponibles:
- `MENU`
- `ENTER <entity_type>`
- `CREATE <entity_type>`
- `UPDATE <entity_type>`
- `DELETE <entity_type>`
- `GET <entity_type> <id>`
- `LIST <entity_type>`
- `BACK`
- `EXIT`

Estado MVP:
- Solo `CREATE product` hace `POST` real a `/API/1.1/ProductoVentaBean`.
- El resto de operaciones y entidades se mantienen en modo `stub`.
- Si el server esta en `IS_PROD=false`, la API devolvera `403` para mutaciones.

## Tests

```bash
pytest -q
```

Suites por marcador:

```bash
pytest -m unit
pytest -m integration
pytest -m api_http
pytest -m contract
```

## Notas
- En modo real, la baja de recursos impacta datos reales en Xubio.
- En modo real, el cliente requiere doble confirmacion para BAJA.
- `PUT /API/1.1/remitoVentaBean/{id}` se mantiene como extension local de compatibilidad;
  el contrato Swagger oficial para update de remito es `PUT /API/1.1/remitoVentaBean`
  con `transaccionId` en el body.
- Los endpoints `GET .../{id}` de catalogos fuera de Swagger oficial
  (`ProductoCompraBean`, `categoriaFiscal`, `depositos`,
  `identificacionTributaria`, `monedaBean`, `vendedorBean`) se mantienen como extension formal
  del contrato local.
