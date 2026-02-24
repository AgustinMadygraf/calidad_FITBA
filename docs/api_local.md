# API Local (FastAPI)

Este documento describe la API local Xubio-like expuesta por el server FastAPI.

## Base URL
- Local: `http://127.0.0.1:8000`

## Politica de contrato
- API de solo lectura.
- Solo se publican endpoints `GET`.
- CORS declara `allow_methods=["GET", "OPTIONS"]`.
- Metodos no permitidos sobre rutas de recursos (`POST`, `PUT`, `PATCH`, `DELETE`) responden `405 Method Not Allowed`.

## Salud
- `GET /health`
- `GET /API/health`

## Inspeccion de token
- `GET /token/inspect`

## Endpoints de dominio
- Cliente:
  - `GET /API/1.1/clienteBean`
  - `GET /API/1.1/clienteBean/{id}`
- Remito venta:
  - `GET /API/1.1/remitoVentaBean`
  - `GET /API/1.1/remitoVentaBean/{id}`
- Producto:
  - `GET /API/1.1/ProductoVentaBean`
  - `GET /API/1.1/ProductoVentaBean/{id}`
  - `GET /API/1.1/ProductoCompraBean`
  - `GET /API/1.1/ProductoCompraBean/{id}`
- Lista de precio:
  - `GET /API/1.1/listaPrecioBean`
  - `GET /API/1.1/listaPrecioBean/{id}`
  - Nota: en llamadas reales reemplazar `{id}` por un entero (ejemplo: `/API/1.1/listaPrecioBean/1`).
- Catalogos:
  - `GET /API/1.1/categoriaFiscal`
  - `GET /API/1.1/categoriaFiscal/{id}`
  - `GET /API/1.1/depositos`
  - `GET /API/1.1/depositos/{id}`
  - `GET /API/1.1/identificacionTributaria`
  - `GET /API/1.1/identificacionTributaria/{id}`
  - `GET /API/1.1/monedaBean`
  - `GET /API/1.1/monedaBean/{id}`
  - `GET /API/1.1/vendedorBean`
  - `GET /API/1.1/vendedorBean/{id}`
- Comprobantes de venta:
  - `GET /API/1.1/comprobanteVentaBean`
  - `GET /API/1.1/comprobanteVentaBean/{id}`

## Cache de lectura
- Cache-aside en operaciones `GET`.
- Configuracion centralizada en `src/shared/config.py`:
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
  - `XUBIO_GET_CACHE_ENABLED`

## Contrato OpenAPI
- Archivo generado localmente: `docs/swagger.json`.

## Arranque del servidor
- `run.py` usa `APP_HOST`/`APP_PORT` (default `127.0.0.1:8000`).
- Si el puerto configurado esta ocupado, intenta automaticamente con el siguiente puerto libre.
