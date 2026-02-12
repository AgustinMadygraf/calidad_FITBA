# Xubio API - Referencia rapida

## Resumen
Xubio expone una API REST para integrar emision de comprobantes electronicos y
otras operaciones sin reinventar funcionalidad existente. La API usa OAuth2 con
`client_credentials` y `Client-ID` y `Secret-ID` para obtener un `access_token`.

Documentacion oficial:
- `https://xubio.com/API/documentation/index.html`

## Que es una API REST
REST es un estilo de arquitectura que utiliza los verbos HTTP para realizar
operaciones CRUD:
- Alta: `POST`
- Baja: `DELETE`
- Modificacion: `PUT`
- Consulta: `GET`

## Que es OAuth2
OAuth2 permite que una aplicacion acceda a datos u operaciones de otro servicio
sin compartir credenciales de usuario. Se basa en la emision de un token de
acceso con tiempo de vida limitado.

## Pasos operativos
1. Dar de alta tu App Cliente en Xubio y obtener `client-id` y `secret-id`.
2. Obtener un `access_token` valido con `client_credentials`.
3. Usar el `access_token` en el header `Authorization: Bearer`.
4. Si el `access_token` es invalido, pedir uno nuevo y reintentar.

### Endpoint de token
`https://xubio.com/API/1.1/TokenEndpoint`

### Ejemplo con curl
```bash
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'grant_type=client_credentials' \
  --user TU_CLIENT_ID:TU_SECRET_ID \
  https://xubio.com/API/1.1/TokenEndpoint
```

### Respuesta esperada
```json
{"scope":"","expires_in":"3600","token_type":"Bearer","access_token":"TU_ACCESS_TOKEN"}
```

## Uso del access_token en recursos
El `access_token` se envia en el header del request:
`Authorization: Bearer TU_ACCESS_TOKEN`

Ejemplo con curl:
```bash
curl -X GET --header "Accept: application/json" \
  --header "Authorization: Bearer TU_ACCESS_TOKEN" \
  "https://xubio.com/API/1.1/clienteBean"
```

## Token invalido
Cuando el `access_token` deje de ser valido, la API puede responder con:
```json
{"error":"invalid_token","error_description":"token died"}
```
En ese caso, repetir el paso 2 para obtener un token nuevo y reintentar el request.

## Estrategias de refresh
- Pedir token en cada request.
- Renovar el token cuando la API responda `401/403`.

## Endpoints usados en este proyecto (Xubio)
- `https://xubio.com/API/1.1/TokenEndpoint`
- `https://xubio.com/API/1.1/clienteBean`
- `https://xubio.com/API/1.1/remitoVentaBean`
- `https://xubio.com/API/1.1/ProductoVentaBean`
- `https://xubio.com/API/1.1/ProductoCompraBean`
- `https://xubio.com/API/1.1/depositos`
- `https://xubio.com/API/1.1/listaPrecioBean`

Nota: Xubio es sensible a mayusculas en algunos endpoints. Ejemplo: `ProductoVentaBean`.

## Lista de Precio y dependencias (uso en este proyecto)
- `listaPrecioBean` se trata como catalogo de referencia con operaciones CRUD.
- `Cliente` puede depender de ese catalogo via `listaPrecioVenta`.
- `RemitoVenta` puede depender de ese catalogo via `listaPrecioId`.
- No se implementaron dependencias inversas (por ejemplo, "que clientes usan una lista")
  dentro de esta API local.

## Estado de relevamiento y pendientes
- Relevamiento completo contra Swagger oficial (Xubio) en:
  - `docs/relevamiento_endpoints_xubio.md`
- Ese documento incluye:
  - endpoints cubiertos vs pendientes,
  - desvios de contrato detectados,
  - To Do List priorizada para cierre de brecha.
