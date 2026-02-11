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
- `GET /API/1.1/remitoVentaBean/{id}`
- `PUT /API/1.1/remitoVentaBean/{id}`
- `DELETE /API/1.1/remitoVentaBean/{id}`

Validaciones relevantes:
- `clienteId` es requerido.
- `listaPrecioId` (si se informa) debe existir.
- `productoId` en items es requerido.
- `depositoId` (cabecera o item) debe existir si se informa.

## Productos
- `GET /API/1.1/productoVentaBean`
- `GET /API/1.1/productoVentaBean/{id}`
- `GET /API/1.1/productoCompraBean`
- `GET /API/1.1/productoCompraBean/{id}`

Nota: Xubio es sensible a mayusculas en algunos endpoints.

## Depositos
- `GET /API/1.1/depositos`
- `GET /API/1.1/depositos/{id}`

## Listas de precio
- `GET /API/1.1/listaPrecioBean`
- `GET /API/1.1/listaPrecioBean/{id}`

## Debug (solo en IS_PROD=false)
- `GET /debug/clienteBean`
