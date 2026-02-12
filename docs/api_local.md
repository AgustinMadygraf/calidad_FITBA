# API Local (FastAPI)

Este documento describe la API local Xubio-like expuesta por el server FastAPI.

## Base URL
- Local: `http://localhost:8000`

## Salud
- `GET /health`

Respuesta:
```json
{"status":"ok"}
```

## Inspeccion de token
- `GET /token/inspect`

Respuesta (ejemplo):
```json
{
  "token_preview": "AZputw...0z04",
  "expires_in_seconds": 3590,
  "expires_at": 1700000000,
  "from_cache": true
}
```

## Cliente
- `GET /API/1.1/clienteBean`
- `POST /API/1.1/clienteBean`
- `GET /API/1.1/clienteBean/{id}`
- `PUT /API/1.1/clienteBean/{id}`
- `DELETE /API/1.1/clienteBean/{id}`

## Categoria fiscal
- `GET /API/1.1/categoriaFiscal`
- `GET /API/1.1/categoriaFiscal/{id}`

Ejemplo (crear):
```json
{
  "razonSocial": "ACME SA",
  "cuit": "30-12345678-9"
}
```

Validaciones relevantes:
- `listaPrecioVenta` (si se informa) debe tener `ID` o `id` valido y existir en Xubio.

## Remito Venta
- `GET /API/1.1/remitoVentaBean`
- `POST /API/1.1/remitoVentaBean`
- `PUT /API/1.1/remitoVentaBean` (contrato Swagger oficial, requiere `transaccionId` en body)
- `GET /API/1.1/remitoVentaBean/{id}`
- `PUT /API/1.1/remitoVentaBean/{id}` (extension local de compatibilidad)
- `DELETE /API/1.1/remitoVentaBean/{id}`

Validaciones relevantes:
- `clienteId` es requerido.
- `listaPrecioId` (si se informa) debe existir.
- `productoId` en items es requerido.
- `depositoId` (cabecera o item) debe existir si se informa.

## Productos
- `GET /API/1.1/ProductoVentaBean`
- `POST /API/1.1/ProductoVentaBean`
- `GET /API/1.1/ProductoVentaBean/{id}`
- `PUT /API/1.1/ProductoVentaBean/{id}`
- `PATCH /API/1.1/ProductoVentaBean/{id}`
- `DELETE /API/1.1/ProductoVentaBean/{id}`
- `GET /API/1.1/ProductoCompraBean`
- `GET /API/1.1/ProductoCompraBean/{id}`

Nota: Xubio es sensible a mayusculas en algunos endpoints.

## Depositos
- `GET /API/1.1/depositos`
- `GET /API/1.1/depositos/{id}`

## Identificaciones tributarias
- `GET /API/1.1/identificacionTributaria`
- `GET /API/1.1/identificacionTributaria/{id}`

## Listas de precio
- `GET /API/1.1/listaPrecioBean`
- `POST /API/1.1/listaPrecioBean`
- `GET /API/1.1/listaPrecioBean/{id}`
- `PUT /API/1.1/listaPrecioBean/{id}`
- `PATCH /API/1.1/listaPrecioBean/{id}`
- `DELETE /API/1.1/listaPrecioBean/{id}`

## Monedas
- `GET /API/1.1/monedaBean`
- `GET /API/1.1/monedaBean/{id}`

## Extensiones formales fuera de Swagger oficial
- `GET /API/1.1/ProductoCompraBean/{id}`
- `GET /API/1.1/categoriaFiscal/{id}`
- `GET /API/1.1/depositos/{id}`
- `GET /API/1.1/identificacionTributaria/{id}`
- `GET /API/1.1/monedaBean/{id}`

Politica:
- Estas rutas se mantienen como contrato local estable por compatibilidad y usabilidad.
- No reemplazan el contrato Swagger oficial; son una extension documentada de esta API local.

## Cache de lectura (modo `IS_PROD=false`)
- `GET` opera con cache-aside sobre Xubio:
  - hit: responde desde cache.
  - miss: consulta Xubio y persiste en cache.
- TTL/configuracion centralizada en `src/shared/config.py`:
  - `XUBIO_CLIENTE_LIST_TTL`
  - `XUBIO_REMITO_LIST_TTL`
  - `XUBIO_PRODUCTO_LIST_TTL`
  - `XUBIO_DEPOSITO_LIST_TTL`
  - `XUBIO_MONEDA_LIST_TTL`
  - `XUBIO_LISTA_PRECIO_LIST_TTL`
  - `XUBIO_CATEGORIA_FISCAL_LIST_TTL`
  - `XUBIO_IDENTIFICACION_TRIBUTARIA_LIST_TTL`
  - `XUBIO_GET_CACHE_ENABLED` (override general de cache on/off).
- En catalogos (`monedaBean`, `listaPrecioBean`, `categoriaFiscal`,
  `identificacionTributaria`, `depositos`), `GET /{id}` resuelve desde la lista
  cacheada + busqueda por ID.

## Mutaciones por entorno
- `IS_PROD=false`: `POST/PUT/PATCH/DELETE` responden `403`.
- `IS_PROD=true`: mutaciones habilitadas contra Xubio.

Dependencias funcionales en esta API local:
- `Cliente` puede referenciar `listaPrecioVenta` (opcional).
- `RemitoVenta` puede referenciar `listaPrecioId` (opcional).
- Cuando se informan esos campos, se valida existencia contra `listaPrecioBean/{id}`.
- `listaPrecioBean` no requiere `clienteId`, `transaccionId` ni `productoId`
  para su lectura.

## Debug (solo en IS_PROD=false)
- `GET /debug/clienteBean`

## Relevamiento Xubio oficial
- Ver estado de cobertura contra Swagger oficial y backlog de endpoints:
  - `docs/relevamiento_endpoints_xubio.md`
