# TODO Proyecto (actualizado 2026-02-26)

Ver completadas en `docs/todo.done.md`.

## Pendiente (puede avanzarse sin decisiones externas)
- [ ] Persistir sesiones/transacciones OIDC en almacenamiento compartido (no in-memory).
- [ ] Endurecer CSRF para endpoints mutables autenticados.
- [ ] Agregar pruebas E2E backend para expiracion de sesion y flujos de error OIDC.

## Pendiente (requiere definicion)
- [ ] CORS definitivo por origen exacto de frontend.
- [ ] Estrategia final de validacion `id_token`:
  - [ ] mantener `tokeninfo` (simple)
  - [ ] migrar a validacion local con JWKS (recomendado para produccion estricta)

## Preguntas abiertas para cerrar
1. ¿Aprobas migrar validacion de `id_token` a JWKS local (en lugar de `tokeninfo`)?
