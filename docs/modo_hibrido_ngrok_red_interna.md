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
- `SERVER_LAN_IP=192.168.55.102`
- `NGROK_DOMAIN=https://confined-unexcused-garland.ngrok-free.dev`

## Configuración base sugerida
```bash
APP_HOST=0.0.0.0
APP_PORT=8000
FRONTEND_CORS_ORIGINS=http://127.0.0.1:8000,http://192.168.55.102:8000,https://confined-unexcused-garland.ngrok-free.dev
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
export SERVER_LAN_IP="192.168.55.102"
export BACKEND_PORT="8000"
export NGROK_DOMAIN="https://confined-unexcused-garland.ngrok-free.dev"
export FRONTEND_INTERNAL_ORIGIN="http://${SERVER_LAN_IP}:${BACKEND_PORT}"
export FRONTEND_NGROK_ORIGIN="$NGROK_DOMAIN"

APP_HOST=0.0.0.0 \
APP_PORT="$BACKEND_PORT" \
FRONTEND_CORS_ORIGINS="http://127.0.0.1:${BACKEND_PORT},${FRONTEND_INTERNAL_ORIGIN},${FRONTEND_NGROK_ORIGIN}" \
python run.py
```

### Arranque ngrok
```bash
ngrok http http://127.0.0.1:8000
```

### Validaciones rápidas
```bash
# Local
curl -i "http://127.0.0.1:8000/health"

# LAN
curl -i "http://192.168.55.102:8000/health"

# ngrok
curl -i "https://confined-unexcused-garland.ngrok-free.dev/health"
```

## ¿Qué deberíamos hacer para despejar dudas?
1. Confirmar red autorizada interna
- Validar CIDR exacto de fábrica (ej. `192.168.55.0/24`) con IT.

2. Confirmar el punto de control de seguridad
- Definir si las reglas se aplican en host firewall, firewall corporativo o ambos.

3. Definir matriz de acceso por canal
- Quién accede por LAN, quién por ngrok, desde qué origen y a qué rutas/puertos.

4. Cerrar política CORS final
- Listar explícitamente orígenes internos reales y origen(es) ngrok permitidos.

5. Endurecer canal ngrok
- Verificar features disponibles en la cuenta (auth, policies, allowlists) y activarlas.

6. Ejecutar pruebas positivas y negativas
- Positivas: acceso válido por LAN y ngrok.
- Negativas: acceso desde origen no permitido / red no autorizada.

7. Definir runbook de operación y contingencia
- Arranque normal híbrido, validaciones post-arranque, y procedimiento ante caída de ngrok o cambios de red.

## Dudas (al final)
1. ¿Cuál es la subred/CIDR exacta autorizada para LAN de fábrica?
2. ¿Qué controles específicos de ngrok están disponibles en el plan actual?
3. ¿Qué orígenes de frontend se deben permitir en producción (lista cerrada)?
4. ¿Quién gestiona firewall de host y firewall corporativo?
5. ¿Se requiere HTTPS interno adicional al HTTPS de ngrok?
