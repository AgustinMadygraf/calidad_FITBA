# Arquitectura

Este proyecto aplica Clean Architecture con separacion de responsabilidades.

## Capas
- `src/entities/`: entidades de dominio (dataclasses) y helpers comunes.
- `src/use_cases/`: casos de uso y validaciones de negocio.
- `src/interface_adapter/`: controllers/handlers y schemas (Pydantic).
- `src/infrastructure/`: gateways HTTPX, FastAPI, memoria.
- `src/shared/`: configuracion y logging.

## Dependencias (direccion)
- `entities` no depende de otras capas.
- `use_cases` depende de `entities` y de puertos (`use_cases/ports`).
- `interface_adapter` traduce entre formatos externos y casos de uso.
- `infrastructure` implementa los puertos.

## CLI AS400 (modularizacion)
- `src/use_cases/terminal_cli.py`:
  - reglas puras del flujo CLI (aliases, parseo de comandos, validacion de entity, plan de accion).
  - armado/validacion de payload de producto sin IO de consola ni red.
- `src/use_cases/terminal_cli_product.py` + `src/use_cases/ports/terminal_cli_product_gateway.py`:
  - caso de uso para `create_product`.
  - puerto explicito para desacoplar la operacion de infraestructura HTTP.
- `src/interface_adapter/presenter/terminal_cli_presenter.py`:
  - render de menu, prompt y formateo textual del estado.
- `src/interface_adapter/controllers/terminal_cli.py`:
  - orquestacion de IO de consola, dispatch de comandos y coordinacion de use cases.
- `src/infrastructure/httpx/terminal_cli_gateway_xubio.py`:
  - implementacion concreta del puerto con HTTPX + OAuth2 client_credentials.

Direccion de dependencias CLI:
- controller -> use_cases + presenter
- infrastructure -> use_cases (implementa puertos)
- use_cases no depende de infrastructure ni de presenter

## Puertos y Gateways
- Cada entidad externa tiene un port (Protocol) en `src/use_cases/ports/`.
- Los gateways HTTPX implementan llamadas a Xubio.
- `IS_PROD=false` y `IS_PROD=true` usan gateways HTTPX; cambia la politica de cache/mutaciones.

## Validaciones clave
- Remito venta:
  - `clienteId` requerido.
  - `listaPrecioId` (si existe) debe existir.
  - `productoId` en items requerido.
  - `depositoId` (cabecera o item) debe existir si se informa.
- Cliente:
  - `listaPrecioVenta` (si existe) debe tener `ID` o `id` valido y existir.

## Dependencias de Lista de Precio
En la implementacion actual:
- `ListaPrecio` expone CRUD (`list/get/create/update/delete`) por su gateway.
- `Cliente` depende de `ListaPrecio` de manera opcional:
  - campo: `cliente.cuentas.listaPrecioVenta`
  - validacion: `src/use_cases/cliente.py`
- `RemitoVenta` depende de `ListaPrecio` de manera opcional:
  - campo: `remito.relaciones.listaPrecioId`
  - validacion: `src/use_cases/remito_venta.py`
- `ListaPrecio` no depende de otras entidades de negocio para validarse.

## Token y autenticacion
- OAuth2 `client_credentials` con `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID`.
- Endpoint por defecto: `https://xubio.com/API/1.1/TokenEndpoint`.
- Refresh automatico ante `invalid_token`.

## Configuracion
- `.env` mantiene solo credenciales/DB: `DATABASE_URL`, `XUBIO_CLIENT_ID`, `XUBIO_SECRET_ID`.
- Configuracion de runtime (modo, host/port, endpoint token y TTL/cache) en `src/shared/config.py`.

## Modo real vs mock
- `IS_PROD=false`: gateways HTTPX Xubio + cache-aside en `GET` y mutaciones bloqueadas (`403`).
- `IS_PROD=true`: gateways HTTPX Xubio sin cache de lectura y mutaciones habilitadas.

## Trazabilidad de cobertura
- Estado de cobertura de endpoints oficiales Xubio y To Do List en:
  - `docs/relevamiento_endpoints_xubio.md`
