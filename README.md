# FITBA Xubio-like (MVP)

Monorepo Python con 2 componentes:
- FastAPI (API local Xubio-like).
- CLI estilo terminal AS400.

Estructura Clean Architecture (resumen):
- `src/entities/`: esquemas y entidades.
- `src/use_case/`: casos de uso.
- `src/interface_adapter/`: controllers (API/CLI), gateways y presenters.
- `src/infrastructure/`: DB y repositorios.
- `src/shared/`: helpers comunes (config/logger).

El MVP implementa PRODUCTO de forma funcional y deja stubs para el resto.

## Resumen Xubio API
Xubio expone una API REST para integrar emisión de comprobantes electrónicos y otras operaciones sin reinventar funcionalidad existente.
La API usa OAuth2 con `client_credentials` y se autentica con `Client-ID` y `Secret-ID` para obtener un `access_token`.
Referencia rapida en `docs/xubio.md`.

## Documentación interna (técnica)
- Estilo REST: operaciones CRUD vía HTTP (`POST`, `GET`, `PUT`, `DELETE`).
- Autenticación: OAuth2 `client_credentials` con `Client-ID` y `Secret-ID`.
- Token: se solicita contra el endpoint de Xubio y tiene un TTL de 3600 segundos.
- Estrategias de refresh: pedir token en cada request o renovar ante `401/403` al consumir recursos.

## Requisitos para módulo de autenticación
- `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID` obligatorios en modo real.
- Endpoint de token: `https://xubio.com/API/1.1/TokenEndpoint`.
- `grant_type=client_credentials`.
- Header `Authorization: Basic base64(client_id:secret_id)`.
- Respuesta esperada incluye `access_token`, `token_type=Bearer`, `expires_in=3600`.

## Pasos operativos (curl)
Solicitud de token:

```bash
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'grant_type=client_credentials' \
  --user TU_CLIENT_ID:TU_SECRET_ID \
  https://xubio.com/API/1.1/TokenEndpoint
```

Respuesta esperada:

```json
{"scope":"","expires_in":"3600","token_type":"Bearer","access_token":"TU_ACCESS_TOKEN"}
```

Uso del token en un recurso:
```bash
curl -X GET --header "Accept: application/json" \
  --header "Authorization: Bearer TU_ACCESS_TOKEN" \
  "https://xubio.com/API/1.1/clienteBean"
```

Si el token expiro, la API responde:
```json
{"error":"invalid_token","error_description":"token died"}
```
En ese caso, pedir un token nuevo y reintentar el request.

## Requisitos
- Python 3.11+
- MySQL (para uso normal)

## Instalacion

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Variables de entorno

```
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/xubio_like
IS_PROD=false
XUBIO_CLIENT_ID=...
XUBIO_SECRET_ID=...
DISABLE_DELETE_IN_REAL=true
PORT=8000

# Cliente
IS_PROD=false
BASE_URL=http://localhost:8000
```

Nota: `IS_PROD` acepta `true/false`, `1/0`, `yes/no`.
En modo real, `XUBIO_BASE_URL`, `XUBIO_TOKEN_ENDPOINT` y `XUBIO_PRODUCT_ENDPOINT`
estan hardcodeados en `src/interface_adapter/gateways/real_xubio_api_client.py`.

Modo en cliente y servidor:
- `IS_PROD=false`: el cliente consume la API local (`BASE_URL`) con formato Xubio y el server usa mock/local DB.
- `IS_PROD=true`: el cliente consume Xubio en forma directa y el server usa cliente real de Xubio.

En modo real, el cliente requiere `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID`.

## Ejecutar servidor

```bash
uvicorn src.infrastructure.fastapi.api:app --reload --port 8000
```

```bash
python -m src.infrastructure.fastapi.api
```

```bash
python run.py
```

## Ejecutar cliente

```bash
python -m src.interface_adapter.controller.cli
```

Override por argumento (prioridad sobre `.env`):

```bash
python -m src.interface_adapter.controller.cli --IS_PROD=true
python -m src.interface_adapter.controller.cli --IS_PROD=false
```

Replica Xubio local (MVP, sin token) en FastAPI:
- `GET /API/1.1/ProductoVentaBean`
- `GET /API/1.1/ProductoVentaBean/{id}`
- `POST /API/1.1/ProductoVentaBean`
- `PATCH /API/1.1/ProductoVentaBean/{id}`
- `DELETE /API/1.1/ProductoVentaBean/{id}`
- `GET /API/1.1/UnidadMedidaBean`
- `GET /API/1.1/UnidadMedidaBean/{id}`
- `POST /API/1.1/UnidadMedidaBean`
- `PATCH /API/1.1/UnidadMedidaBean/{id}`
- `DELETE /API/1.1/UnidadMedidaBean/{id}`

Cliente (MVP, in-memory):
- `GET /API/1.1/clienteBean`
- `POST /API/1.1/clienteBean`
- `GET /API/1.1/clienteBean/{id}`
- `PUT /API/1.1/clienteBean/{id}`
- `DELETE /API/1.1/clienteBean/{id}`

Nota: si `IS_PROD=true`, estos endpoints actuan como proxy hacia Xubio real (base URL hardcodeada).
Si `IS_PROD=false`, se usa un gateway in-memory temporal (hasta tener DB real).

## Ejemplo de sesion CLI

```
=== TERMINAL FITBA/XUBIO ===
30 - productoVenta
43 - unidadMedida

> 1
=== PRODUCTO ===
1) Alta
2) Modificar
3) Baja
4) Consultar por ID
5) Listar
6) Volver
```

## Tests

```bash
pytest -q
```

## Notas
- En modo real, la baja de recursos impacta datos reales en Xubio.
- En modo real, el cliente exige doble confirmacion para BAJA.
- La tabla principal de persistencia es `productoVenta`.
