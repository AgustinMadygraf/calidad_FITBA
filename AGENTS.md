## Xubio-like (estructura base, sin integracion real)

### Decisiones acordadas
- Monorepo Python con `server/` (FastAPI) y `client/` (CLI AS400).
- MVP: PRODUCTO funcional. Otros entity_type en menu como stub.
- Modo mock vs real por env: `IS_PROD=true|false`.
- Tabla unica `integration_records` para iterar rapido.

### Base de datos (MySQL)
Tabla `integration_records`:
- `id` (BIGINT autoincrement)
- `created_at` (datetime UTC)
- `updated_at` (datetime UTC)
- `entity_type` (varchar)
- `operation` (varchar)
- `external_id` (varchar nullable)
- `payload_json` (JSON)
- `status` (varchar)
- `last_error` (text nullable)
Indices:
- `index(entity_type, external_id)`
- `index(entity_type, status)`

### API local (FastAPI)
- `POST /terminal/execute`
- `POST /sync/pull/product`
- `POST /sync/push/product`
- `GET /health`

### Terminal commands (internos)
- `MENU`
- `ENTER <entity_type>`
- `CREATE <entity_type>`
- `UPDATE <entity_type>`
- `DELETE <entity_type>`
- `GET <entity_type> <id>`
- `LIST <entity_type>`
- `BACK`

### Restricciones
- No clonar toda la API de Xubio.
- En modo real, BAJA debe tener doble confirmacion en el cliente.
- Autenticacion real: OAuth2 client_credentials.
