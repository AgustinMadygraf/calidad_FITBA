# Arquitectura

- FastAPI + Clean Architecture + MySQL.
- Repositorios: in-memory para tests y MySQL para runtime.
- UoW por request.

## Carpetas
- `servidor/app`: API y routers
- `servidor/application`: casos de uso y DTOs
- `servidor/domain`: entidades y validaciones
- `servidor/infrastructure`: DB y repos
- `cliente`: CLI AS400-style
