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
XUBIO_MODE=mock  # mock | real
XUBIO_BASE_URL=https://xubio.com/API/1.1
XUBIO_TOKEN_ENDPOINT=https://xubio.com/API/1.1/TokenEndpoint
XUBIO_CLIENT_ID=...
XUBIO_SECRET_ID=...
XUBIO_PRODUCT_ENDPOINT=/Products  # TODO confirmar endpoint real
DISABLE_DELETE_IN_REAL=true

# Cliente
BASE_URL=http://localhost:8000
```

## Ejecutar servidor

```bash
python -m server.app
```

## Ejecutar cliente

```bash
python -m client.app
```

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
