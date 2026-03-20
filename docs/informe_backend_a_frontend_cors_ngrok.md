# Informe Backend -> Frontend: Incidente CORS (LAN vs ngrok)

Fecha: 2026-02-24  
Equipo emisor: Backend  
Equipo destinatario: Frontend

## Resumen corto
Se detectó bloqueo CORS porque el frontend cargado en LAN (`http://10.176.61.33:8000`) está llamando a API por ngrok (`https://confined-unexcused-garland.ngrok-free.dev/...`) en lugar de usar mismo origen LAN.

Conclusión operativa: el problema es de configuración de consumo en frontend (`baseURL`/runtime config), no de endpoint funcional de backend LAN.

## Evidencia
Error de navegador reportado:
- `Access to fetch ... from origin 'http://10.176.61.33:8000' has been blocked by CORS policy`
- `No 'Access-Control-Allow-Origin' header is present on the requested resource`
- URL fallida: `https://confined-unexcused-garland.ngrok-free.dev/API/1.1/remitoVentaBean`

## Diagnóstico técnico backend
1. El backend LAN está disponible en `http://10.176.61.33:8000`.
2. CORS del backend fue reforzado en runtime para incluir orígenes LAN/localhost.
3. El error actual ocurre en request a dominio ngrok (cross-origin), no en same-origin LAN.
4. Si frontend en LAN llama a ngrok, el preflight depende de la respuesta del canal ngrok/edge.

## Requerimiento al equipo frontend (acción)
1. En modo red interna, configurar API en mismo origen:
- recomendado: `baseURL` relativo `"/API/1.1"`
- alternativa: `http://10.176.61.33:8000/API/1.1`

2. No usar ngrok como `baseURL` cuando el frontend se sirve en LAN interna.

3. Confirmar variables finales efectivas en runtime/build:
- `VITE_API_BASE_URL` (o equivalente)
- valor final utilizado por `httpClient` al abrir `http://10.176.61.33:8000`

4. Adjuntar evidencia de cierre:
- captura Network de request final exitosa a `/API/1.1/remitoVentaBean`
- confirmar que ya no aparece preflight bloqueado por CORS

## Criterio de aceptación
Se considera resuelto cuando:
1. `remitos` carga correctamente desde `http://10.176.61.33:8000`.
2. No hay errores CORS en consola.
3. La request va a mismo origen LAN (no a ngrok) en modo red interna.

## Nota de coordinación
Si se requiere soporte remoto externo, se puede usar modo `full/ngrok`, pero debe definirse explícitamente como entorno distinto al de operación LAN interna.
