# Modo Híbrido: ngrok + Red Interna de Fábrica

## Objetivo
Operar en modo complementario:
- Acceso interno desde la red de fábrica.
- Acceso remoto vía `ngrok`.

## Certezas
1. `ngrok` y acceso LAN pueden convivir sobre el mismo backend.
2. Para acceso LAN, el backend debe escuchar en red (`APP_HOST=0.0.0.0` o IP LAN específica).
3. CORS debe incluir orígenes internos y origen ngrok autorizados.
4. CORS no reemplaza seguridad de red: el control real debe estar en firewall/perímetro y autenticación.
5. Debe existir segmentación de riesgo por canal:
- LAN: restringir por subred interna autorizada.
- ngrok: reforzar con controles adicionales (autenticación, políticas, rate-limit).
6. La trazabilidad en logs por canal de acceso (interno/ngrok) es necesaria para operación segura.
7. En este entorno se detectó:
- `SERVER_LAN_IP=192.168.55.102` (segmento `192.168.x.x`).
- `NGROK_DOMAIN=https://confined-unexcused-garland.ngrok-free.dev`.
8. El segmento `192.168.x.x` tiene restricciones y no llega a toda la fábrica.
9. El segmento `10.176.61.x` sí tiene alcance desde toda la fábrica.
10. `http://10.176.61.33:8000` es acceso por IP privada de red interna (RFC1918), no IP pública de Internet.
11. Con el estado actual (`run_server.py --mode red-interna`) el backend expone HTTP en puerto `8000`; no hay TLS nativo en Uvicorn.
12. Para HTTPS interno, el patrón recomendado es terminar TLS en un reverse proxy en `443` y reenviar al backend en `127.0.0.1:8000`.

## Configuración base sugerida
```bash
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_CORS_ORIGINS=http://127.0.0.1:8000,http://10.176.61.<IP_SERVIDOR>:8000,https://confined-unexcused-garland.ngrok-free.dev
```

## Comandos operativos (copy-paste)
### Selector de modo en entry point
```bash
# Default (si no se pasa --mode): ngrok
./run.sh

# Solo ngrok
./run.sh --mode ngrok

# Solo red interna
./run.sh --mode red-interna

# Ambos canales (ngrok + LAN)
./run.sh --mode full
```

### Arranque backend
```bash
source venv/bin/activate
export SERVER_LAN_IP="10.176.61.<IP_SERVIDOR>"
export BACKEND_PORT="8000"
export NGROK_DOMAIN="https://confined-unexcused-garland.ngrok-free.dev"
export FRONTEND_INTERNAL_ORIGIN="http://${SERVER_LAN_IP}:${BACKEND_PORT}"
export FRONTEND_NGROK_ORIGIN="$NGROK_DOMAIN"

APP_HOST=0.0.0.0 \
APP_PORT="$BACKEND_PORT" \
FRONTEND_CORS_ORIGINS="http://127.0.0.1:${BACKEND_PORT},${FRONTEND_INTERNAL_ORIGIN},${FRONTEND_NGROK_ORIGIN}" \
python run_server.py
```

### Arranque ngrok
```bash
ngrok http http://127.0.0.1:8000
```

### Validaciones rápidas
```bash
# Local
curl -i "http://127.0.0.1:8000/health"

# LAN fábrica (usar IP 10.176.61.x del servidor)
curl -i "http://10.176.61.<IP_SERVIDOR>:8000/health"

# ngrok
curl -i "https://confined-unexcused-garland.ngrok-free.dev/health"
```

## ¿Qué deberíamos hacer para despejar dudas?
1. Confirmar IP operativa del servidor en `10.176.61.x`
- Definir IP fija o reserva DHCP para evitar cambios.

2. Confirmar red autorizada interna
- Validar CIDR exacto de fábrica (ej. `10.176.61.0/24` u otro) con IT.

3. Confirmar el punto de control de seguridad
- Definir si las reglas se aplican en host firewall, firewall corporativo o ambos.

4. Definir matriz de acceso por canal
- Quién accede por LAN, quién por ngrok, desde qué origen y a qué rutas/puertos.

5. Cerrar política CORS final
- Listar explícitamente orígenes internos reales y origen(es) ngrok permitidos.

6. Endurecer canal ngrok
- Verificar features disponibles en la cuenta (auth, policies, allowlists) y activarlas.

7. Ejecutar pruebas positivas y negativas
- Positivas: acceso válido por LAN y ngrok.
- Negativas: acceso desde origen no permitido / red no autorizada.

8. Definir runbook de operación y contingencia
- Arranque normal híbrido, validaciones post-arranque, y procedimiento ante caída de ngrok o cambios de red.

## Dudas (al final)
1. ¿Cuál es la IP exacta del servidor dentro de `10.176.61.x` para operación estable?
2. ¿Qué CIDR exacto de fábrica debemos permitir para acceso interno?
3. ¿Qué controles específicos de ngrok están disponibles en el plan actual?
4. ¿Qué orígenes de frontend se deben permitir en producción (lista cerrada)?
5. ¿Quién gestiona firewall de host y firewall corporativo?
6. ¿Se requiere HTTPS interno adicional al HTTPS de ngrok?
7. ¿IT puede asignar reserva DHCP o IP fija para `10.176.61.33` en el servidor de fábrica?
8. ¿El frontend productivo consumirá `https://<dominio-interno>` (recomendado) o `https://10.176.61.33` (certificados más complejos)?

## Actualización operativa (2026-02-24)
Escenario observado:
- Arranque: `python run_server.py --mode red-interna`
- Bind: `0.0.0.0:8000`
- Acceso LAN detectado: `http://10.176.61.33:8000`
- Frontend dev proxy no disponible (`127.0.0.1:5173`), backend sirve estáticos como fallback.
- `./scripts/setup_modo_hibrido.sh red-interna` detecta `SERVER_IP=10.176.61.33` y CORS interno correcto.
- `NETINFO` mostró:
  - `CLI base_url=https://xubio.com`
  - `Base URL esquema=HTTPS`, `puerto=443`
  - `Puerto local 8000 abierto=si`
  - `Puerto local 443 abierto=si`
  - `IPs LAN detectadas=No detectada`
- HTTPS servidor validado:
  - `curl -ik https://api.madygraf.local/health` -> `200 OK` (con entrada local en `/etc/hosts`).

Implicancias:
- Si cambia la IP LAN del servidor, cambiará la URL por IP.
- Para evitar depender de IP en frontend, usar hostname interno estable (DNS corporativo o `hosts`) y apuntar siempre a ese nombre.
- HTTPS no implica obligatoriamente "mover FastAPI a 443"; normalmente se publica `443` en proxy y FastAPI sigue en `8000` interno.
- Hay un servicio local escuchando en `443`; debe identificarse antes de montar TLS interno definitivo.
- `NETINFO` necesita fallback adicional (`hostname -I`) para detectar mejor IPs LAN en algunos hostnames.

Objetivo recomendado:
```text
Frontend -> https://api.madygraf.local:443 -> Apache (TLS) -> http://127.0.0.1:8000 (FastAPI)
```

## Automatización parcial
Script disponible:
```bash
./scripts/setup_modo_hibrido.sh [ngrok|red-interna|full]
```

Ejemplos:
```bash
./scripts/setup_modo_hibrido.sh full
./scripts/setup_modo_hibrido.sh red-interna
IP_HINT_PREFIX=10.176.61. BACKEND_PORT=8000 NGROK_DOMAIN=confined-unexcused-garland.ngrok-free.dev ./scripts/setup_modo_hibrido.sh full
```

Arranque automático con variables calculadas:
```bash
START_SERVER=true ./scripts/setup_modo_hibrido.sh full
```

## Diagnóstico automático en CLI
Desde la CLI interactiva ahora existe:
- `NETINFO` (alias `RED`)

Muestra automáticamente:
- IPs LAN detectadas y clasificación (privada/pública).
- Esquema/host/puerto del `base_url` del CLI.
- Estado local de puertos `8000` y `443`.
- Recomendaciones para estabilidad (DNS, IP fija/reserva DHCP, TLS en reverse proxy).

## Próximos pasos concretos
1. Confirmar con IT si `10.176.61.33` es reserva DHCP o IP fija.
2. Identificar proceso que usa `443`:
```bash
sudo lsof -i :443 -sTCP:LISTEN -P -n
```
3. Definir hostname interno objetivo (`api.<empresa>.local`) y apuntar frontend a ese nombre.
4. Implementar TLS en reverse proxy `:443 -> 127.0.0.1:8000`.

## HTTPS interno (avance operativo)
Scripts nuevos:
```bash
./scripts/check_https_readiness.sh
./scripts/generate_nginx_https_conf.sh
./scripts/generate_apache_https_vhost.sh
./scripts/detect_443_owner.sh
./scripts/generate_local_tls_cert.sh
./scripts/setup_nginx_https_local.sh
./scripts/setup_apache_https_local.sh
```

Uso recomendado:
```bash
# 1) Chequeo de precondiciones
./scripts/check_https_readiness.sh

# 2) Generar conf base de Nginx (sin aplicar cambios al sistema)
DOMAIN=api.empresa.local \
TLS_CERT_PATH=/etc/ssl/certs/api.empresa.local.crt \
TLS_KEY_PATH=/etc/ssl/private/api.empresa.local.key \
OUT_FILE=/tmp/nginx_api_empresa_local.conf \
./scripts/generate_nginx_https_conf.sh
```

Notas:
- En este host, `443` está en uso por `apache2` (confirmado con `ss/lsof`).
- En este host, Nginx queda como alternativa genérica pero **no recomendada** para el despliegue actual.
- Se mantiene Apache como terminación TLS en `443`.

## Plan acordado (implementación local)
Parámetros confirmados:
- reverse proxy: `apache2` (ya activo en `443`)
- dominio: `api.madygraf.local`
- certificado producción: **CA corporativa**
- certificado local/self-signed: **solo pruebas internas temporales**
- despliegue HTTPS: en esta misma máquina

Flujo recomendado:
```bash
# 1) Identificar dueño de 443
./scripts/detect_443_owner.sh

# 2) Generar cert local (repo)
DOMAIN=api.madygraf.local ./scripts/generate_local_tls_cert.sh

# 3) Generar conf Apache apuntando a FastAPI :8000
DOMAIN=api.madygraf.local ./scripts/setup_apache_https_local.sh
```

Automatización parcial al iniciar backend (`run.py --mode red-interna|full`):
- Siempre muestra `HTTPS readiness` (nginx/apache, 443 en uso, cert/key/conf presentes).
- Si `AUTO_PREPARE_HTTPS=true`, genera automáticamente:
  - cert/key local en `.runtime/tls/`
  - conf nginx en `.runtime/nginx/` (solo artefacto opcional; no camino principal)

Ejemplo:
```bash
export HTTPS_DOMAIN=api.madygraf.local
export AUTO_PREPARE_HTTPS=true
python run.py --mode red-interna
```

Artefactos generados:
- cert: `.runtime/tls/api.madygraf.local.crt`
- key: `.runtime/tls/api.madygraf.local.key`
- apache conf: `.runtime/apache/api.madygraf.local.conf`

Aplicación manual (requiere root):
1. Habilitar módulos Apache: `ssl proxy proxy_http headers`.
2. Copiar `.runtime/apache/api.madygraf.local.conf` a `/etc/apache2/sites-available/api.madygraf.local.conf`.
3. Habilitar sitio Apache.
4. Validar y recargar:
```bash
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## Evidencia automática para IT (IP estable)
Script:
```bash
./scripts/check_ip_stability.sh
```

Qué registra:
- interfaz por defecto, gateway, IP/CIDR LAN, MAC, IP pública.
- si hubo cambio respecto de la ejecución anterior (`changed_ip`).

Archivos:
- estado actual: `/tmp/calidad_fitba_net/ip_state.env`
- historial: `/tmp/calidad_fitba_net/ip_history.log`

## Auditoría automática en SQLite
Cuando el backend inicia en `--mode red-interna` o `--mode full`, guarda una muestra de red en SQLite y compara contra la anterior.

DB por defecto:
- `.runtime/network_audit.sqlite3`

Override:
```bash
export NETWORK_AUDIT_DB="/ruta/custom/network_audit.sqlite3"
```

Consulta rápida desde CLI:
- `NETINFO` (alias `RED`) muestra el último estado de auditoría y si detectó cambio de IP/interfaz/gateway.
