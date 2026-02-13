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

## Observabilidad frontend (MVP)
- `POST /observability/events`

Headers:
- `Content-Type: application/json`

CORS MVP:
- `allow_origins`: `http://127.0.0.1:5173`
- `allow_methods`: `POST`, `OPTIONS`
- `allow_headers`: `Content-Type`

Envelope minimo:
```json
{
  "type": "http_request | route_navigation | page_load | frontend_error",
  "level": "info | warn | error",
  "timestamp": "2026-02-13T11:23:45.120Z",
  "context": {}
}
```

Reglas MVP implementadas:
- Requiere `type`, `level`, `timestamp`, `context`.
- `type` permitido: `http_request`, `route_navigation`, `page_load`, `frontend_error`.
- `level` permitido: `info`, `warn`, `error`.
- `context` debe ser objeto JSON.
- `timestamp` debe ser ISO-8601 UTC.
- Limite de body por evento: `32KB` (`413` si excede).
- En `frontend_error`, si `context.stack` supera `8KB`, se trunca server-side.
- Incluye `requestId` en respuesta y logs.
- Rate-limit basico por IP: `120 req/min` (`429` si excede).

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

## Vendedores
- `GET /API/1.1/vendedorBean`
- `GET /API/1.1/vendedorBean/{id}` (extension local)

Ejemplo de item:
```json
{
  "vendedorId": 0,
  "nombre": "string",
  "apellido": "string",
  "esVendedor": 0,
  "activo": 0
}
```

## Comprobantes de venta
- `GET /API/1.1/comprobanteVentaBean`
- `GET /API/1.1/comprobanteVentaBean/{id}`

Ejemplo de item:
```json
{
  "transaccionid": 0,
  "externalId": "string",
  "nombre": "string",
  "fecha": "2018-12-31",
  "importetotal": 0,
  "cliente": {
    "ID": 0,
    "nombre": "string",
    "codigo": "string",
    "id": 0
  },
  "vendedor": {
    "vendedorId": 0,
    "nombre": "string",
    "apellido": "string",
    "esVendedor": 0,
    "activo": 0
  }
}
```

## Extensiones formales fuera de Swagger oficial
- `GET /API/1.1/ProductoCompraBean/{id}`
- `GET /API/1.1/categoriaFiscal/{id}`
- `GET /API/1.1/depositos/{id}`
- `GET /API/1.1/identificacionTributaria/{id}`
- `GET /API/1.1/monedaBean/{id}`
- `GET /API/1.1/vendedorBean/{id}`

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
  - `XUBIO_VENDEDOR_LIST_TTL`
  - `XUBIO_COMPROBANTE_VENTA_LIST_TTL`
  - `XUBIO_GET_CACHE_ENABLED` (override general de cache on/off).
- En catalogos livianos (`monedaBean`, `categoriaFiscal`,
  `identificacionTributaria`, `depositos`), `GET /{id}` resuelve desde la lista
  cacheada + busqueda por ID.
- En `listaPrecioBean`, `GET /{id}` consulta primero el endpoint detalle oficial
  (`/API/1.1/listaPrecioBean/{id}`) y usa fallback al listado solo ante `5xx`.
- En `comprobanteVentaBean`, `GET /{id}` consulta primero el endpoint detalle
  oficial (`/API/1.1/comprobanteVentaBean/{id}`) y usa fallback al listado solo
  ante `5xx`.

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
