# Informe CORS: Backend -> Frontend

Fecha: 2026-02-24  
Contexto: acceso interno LAN (`red-interna`) en `http://10.176.61.33:8000`

## Resumen ejecutivo
- Se observó bloqueo de navegador por CORS/preflight al navegar en `http://10.176.61.33:8000/remitos`.
- Del lado backend, se reforzó la configuración para incluir orígenes LAN en runtime.
- Falta confirmar desde frontend el `Origin` real de las requests y si existen headers/métodos que disparen preflight con condiciones no contempladas.
- Evidencia frontend recibida: hubo casos con `Origin: http://localhost` y request hacia ngrok.

## Hallazgos backend (confirmados)
1. Middleware CORS activo en FastAPI:
- `allow_origins` dinámico por `FRONTEND_CORS_ORIGINS`.
- `allow_methods=["GET","OPTIONS"]`.
- `allow_headers=["*"]`.

2. Ajuste aplicado en runtime (`run.py`):
- En `red-interna/full`, se agregan automáticamente:
  - `http://127.0.0.1:<port>`
  - `http://<ip_lan_detectada>:<port>`
- También se agregan variantes localhost explícitas:
  - `http://localhost`
  - `http://localhost:5173`
  - `http://127.0.0.1`
  - `http://127.0.0.1:5173`
- En `ngrok/full`, se agrega `NGROK_DOMAIN` (si está seteado).
  - Si viene sin esquema, backend normaliza a `https://...`.
- Se loguea: `CORS runtime origins efectivos: ...`

3. Estado de red backend:
- LAN estable detectada en `10.176.61.33`.
- Auditoría SQLite registrando cambios de IP/interfaz/gateway.

## Evidencia técnica sugerida (backend)
Ejecutar desde backend para validar preflight:

```bash
curl -i -X OPTIONS "http://10.176.61.33:8000/remitos" \
  -H "Origin: http://10.176.61.33:8000" \
  -H "Access-Control-Request-Method: GET"
```

Validar caso localhost:
```bash
curl -i -X OPTIONS "http://10.176.61.33:8000/API/1.1/remitoVentaBean" \
  -H "Origin: http://localhost" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: accept,ngrok-skip-browser-warning"
```

Validar caso ngrok:
```bash
curl -i -X OPTIONS "http://10.176.61.33:8000/API/1.1/remitoVentaBean" \
  -H "Origin: https://confined-unexcused-garland.ngrok-free.dev" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: accept,ngrok-skip-browser-warning"
```

Para simular headers custom (si frontend los envía):

```bash
curl -i -X OPTIONS "http://10.176.61.33:8000/remitos" \
  -H "Origin: http://10.176.61.33:8000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: content-type,authorization,ngrok-skip-browser-warning"
```

## Hipótesis actuales
1. El frontend podría estar haciendo requests con `Origin` distinto al esperado (ej. otro puerto, dominio, ngrok, `file://` o `localhost`).
2. El frontend podría estar enviando headers no simples o método no simple, disparando preflight distinto al validado manualmente.
3. Puede existir Service Worker, proxy dev, o build antigua apuntando a otro `baseURL`.

## Consultas del equipo backend al equipo frontend
Solicitamos respuesta explícita sobre estos puntos:

1. ¿Cuál es el `Origin` exacto del frontend en producción interna?
- Ejemplo esperado: `http://10.176.61.33:8000` o `https://api.empresa.local`.

2. ¿Cuál es el `Request URL` exacto que dispara error CORS?
- Incluir protocolo, host, puerto y path.

3. ¿Qué método HTTP se usa en la request fallida?
- `GET`, `POST`, `PUT`, etc.

4. ¿Qué headers envía el frontend en esa request?
- Especialmente: `Authorization`, `Content-Type`, `X-*`, `ngrok-*`.

5. ¿Qué muestra la pestaña Network del navegador en el preflight (`OPTIONS`)?
- `Request Headers` completos.
- `Response Headers` completos.
- Status code exacto del preflight.

6. ¿Hay Service Worker activo?
- Confirmar si intercepta/fabrica requests.

7. ¿El frontend usa proxy dev (Vite/Webpack) o URL directa en build?
- Si usa proxy, compartir configuración.
- Si usa URL directa, compartir variable final (`VITE_API_URL` o equivalente).

8. ¿Existe mezcla de contenido (`https` frontend llamando `http` backend)?
- Confirmar si hay warnings de Mixed Content.

9. ¿El error ocurre en todas las rutas o sólo en `/remitos`?
- Si es selectivo, listar rutas que fallan y que no fallan.

10. ¿Adjuntan captura HAR o export Network de DevTools?
- Para correlacionar exactamente preflight y respuesta.

## Entregables esperados de frontend
1. Captura HAR de la request fallida.
2. `Origin` final y `baseURL` final usados por frontend.
3. Lista real de headers enviados.
4. Confirmación de método HTTP por endpoint.

## Criterio de cierre
Se considera resuelto cuando:
1. Preflight `OPTIONS` responde 200 con `access-control-allow-origin` correcto.
2. Request final deja de ser bloqueada por navegador.
3. Se documenta el origen definitivo permitido (LAN y/o dominio HTTPS).
