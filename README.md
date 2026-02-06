# FITBA Xubio-like (MVP)

Monorepo Python con 2 componentes:
- `server/`: FastAPI (API local Xubio-like + terminal AS400 style).
- `client/`: CLI estilo terminal AS400.

El MVP implementa PRODUCTO de forma funcional y deja stubs para el resto.

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
estan hardcodeados en `server/infrastructure/clients/real_xubio_api_client.py`.

Modo en cliente y servidor:
- `IS_PROD=false`: el cliente consume la API local (`BASE_URL`) con formato Xubio y el server usa mock/local DB.
- `IS_PROD=true`: el cliente consume Xubio en forma directa y el server usa cliente real de Xubio.

En modo real, el cliente requiere `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID`.

## Ejecutar servidor

```bash
python -m server.app
```

## Ejecutar cliente

```bash
python -m client.app
```

Override por argumento (prioridad sobre `.env`):

```bash
python -m client.app --IS_PROD=true
python -m client.app --IS_PROD=false
```

Replica Xubio local (MVP, sin token) en FastAPI:
- `GET /API/1.1/ProductoVentaBean`
- `GET /API/1.1/ProductoVentaBean/{id}`
- `POST /API/1.1/ProductoVentaBean`
- `PATCH /API/1.1/ProductoVentaBean/{id}`
- `DELETE /API/1.1/ProductoVentaBean/{id}`
- `POST /sync/pull/product/from-xubio` (solo `IS_PROD=false`, sincroniza DB local leyendo Xubio real)

## Ejemplo de sesion CLI

```
=== TERMINAL FITBA/XUBIO ===
1) PRODUCTO
2) CLIENTE (stub)
3) PROVEEDOR (stub)
4) COMPROBANTES (stub)
5) PESADAS (stub)

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
