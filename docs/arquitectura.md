# Arquitectura

Este proyecto aplica Clean Architecture con separacion de responsabilidades.

## Capas
- `src/entities/`: entidades de dominio.
- `src/use_cases/`: casos de uso.
- `src/interface_adapter/`: controllers/presenters/schemas.
- `src/infrastructure/`: FastAPI y gateways HTTPX.
- `src/shared/`: configuracion y logging.

## Direccion de dependencias
- `entities` no depende de otras capas.
- `use_cases` depende de `entities` y puertos.
- `interface_adapter` traduce I/O.
- `infrastructure` implementa puertos.

## API
- Contrato local en modo solo lectura.
- Endpoints publicados de dominio: solo `GET`.
- OpenAPI fuente de verdad: `docs/swagger.json`.

## CLI
- Flujo textual.
- Comandos vigentes: `MENU`, `ENTER`, `GET`, `LIST`, `BACK`, `EXIT`, `DSP`.
- No ejecuta mutaciones.

## Token y autenticacion
- OAuth2 `client_credentials` con `XUBIO_CLIENT_ID` y `XUBIO_SECRET_ID`.
- Endpoint por defecto: `https://xubio.com/API/1.1/TokenEndpoint`.

## Configuracion
- No se usa `IS_PROD`.
- Runtime y cache definidos en `src/shared/config.py`.
