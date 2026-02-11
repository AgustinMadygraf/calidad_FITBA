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

## Puertos y Gateways
- Cada entidad externa tiene un port (Protocol) en `src/use_cases/ports/`.
- Los gateways HTTPX implementan llamadas a Xubio.
- Los gateways in-memory se usan en `IS_PROD=false`.

## Validaciones clave
- Remito venta:
  - `clienteId` requerido.
  - `listaPrecioId` (si existe) debe existir.
  - `productoId` en items requerido.
  - `depositoId` (cabecera o item) debe existir si se informa.
- Cliente:
  - `listaPrecioVenta` (si existe) debe tener `ID` o `id` valido y existir.

## Token y autenticacion
- OAuth2 `client_credentials` con `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID`.
- Endpoint por defecto: `https://xubio.com/API/1.1/TokenEndpoint`.
- Refresh automatico ante `invalid_token`.

## Modo real vs mock
- `IS_PROD=false`: gateways in-memory.
- `IS_PROD=true`: gateways HTTPX reales.
