# TODO Done (actualizado 2026-02-26)

## Realizadas
- [x] Implementado contrato backend de auth:
  - [x] `GET /auth/session`
  - [x] `POST /auth/login/google`
  - [x] `POST /auth/logout`
  - [x] `GET /auth/callback/google`
- [x] Sesion backend con cookie `HttpOnly` + `Path=/` + TTL configurable.
- [x] Inicio de login OIDC en backend con `state`, `nonce`, `PKCE`.
- [x] Callback OIDC con:
  - [x] validacion de `state` y expiracion de transaccion
  - [x] intercambio de `code` por tokens
  - [x] validacion de claims `id_token` (`iss`, `aud`, `exp`, `nonce`)
  - [x] creacion de sesion y redireccion a `redirectPath` interno validado
- [x] CORS ajustado para credenciales y metodo `POST`.
- [x] Tests de contrato/flujo auth en verde.
- [x] Documentacion base y `.env.example` actualizados.
- [x] Observabilidad auth con eventos estructurados y `correlation_id`:
  - [x] `auth.login.start`
  - [x] `auth.login.callback.success`
  - [x] `auth.login.callback.failure`
  - [x] `auth.session.read`
  - [x] `auth.logout`
- [x] CSRF baseline por `Origin` en `POST /auth/login/google` y `POST /auth/logout`.
- [x] Default de cookie en prod ajustado para cross-origin (`SameSite=None` cuando `IS_PROD=true`).
- [x] Fix defensivo CORS: `get_frontend_cors_origins()` ahora fusiona defaults + `FRONTEND_CORS_ORIGINS` para no perder `https://xubio.madygraf.com`.
- [x] Script operativo `scripts/force_backend_8000.sh`:
  - [x] detecta y mata procesos que escuchen en `:8000`
  - [x] arranca backend en `8000` con `run_server.py --mode red-interna`

## Definiciones confirmadas
- [x] Frontend productivo: `https://xubio.madygraf.com`
- [x] Backend productivo: dominio `ngrok` (origen distinto al frontend)
- [x] Topologia: cross-origin (requiere CORS con credenciales)
- [x] Recomendacion tecnica derivada: cookie de sesion con `SameSite=None` y `Secure=true`
