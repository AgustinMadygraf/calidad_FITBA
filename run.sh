#!/usr/bin/env bash

# =============================================================================
# run.sh - Inicia ngrok + FastAPI para el entorno de desarrollo
# =============================================================================
# Uso:
#   ./run.sh              # Inicia en foreground (ver logs en tiempo real)
#   ./run.sh --daemon     # Inicia en background (sin terminal abierta)
#   ./run.sh --mode ngrok         # Solo canal ngrok (default)
#   ./run.sh --mode red-interna   # Solo canal LAN interno
#   ./run.sh --mode full          # ngrok + LAN interno
#   ./run.sh --stop       # Detiene todos los servicios en background
#   ./run.sh --status     # Muestra el estado de los servicios
#   ./run.sh --logs       # Muestra los logs de FastAPI
# =============================================================================

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cargar variables de entorno desde .env si existe
if [ -f ".env" ]; then
    echo -e "\033[0;34mℹ️  Cargando variables desde .env...\033[0m"
    set -a  # Auto-export todas las variables
    # shellcheck disable=SC1091
    source .env
    set +a  # Desactivar auto-export
fi

# Variables configurables vía entorno (con valores por defecto)
NGROK_URL="${NGROK_URL:-confined-unexcused-garland.ngrok-free.dev}"
FASTAPI_PORT="${FASTAPI_PORT:-8000}"
RUN_MODE="${RUN_MODE:-ngrok}"
NGROK_PID_FILE="${NGROK_PID_FILE:-/tmp/ngrok_calidad_fitba.pid}"
FASTAPI_PID_FILE="${FASTAPI_PID_FILE:-/tmp/fastapi_calidad_fitba.pid}"
VENV_PATH="${VENV_PATH:-$SCRIPT_DIR/venv/bin/activate}"

# Archivos de logs (para modo daemon)
FASTAPI_LOG_FILE="${FASTAPI_LOG_FILE:-/tmp/fastapi_calidad_fitba.log}"
NGROK_LOG_FILE="${NGROK_LOG_FILE:-/tmp/ngrok_output.log}"

# =============================================================================
# Funciones de utilidad
# =============================================================================

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# =============================================================================
# Comandos de control (stop, status, logs)
# =============================================================================

cmd_stop() {
    log_info "Deteniendo servicios..."
    
    # Detener FastAPI
    if [ -f "$FASTAPI_PID_FILE" ]; then
        FASTAPI_PID=$(cat "$FASTAPI_PID_FILE")
        if ps -p $FASTAPI_PID > /dev/null 2>&1; then
            kill $FASTAPI_PID 2>/dev/null || true
            rm -f "$FASTAPI_PID_FILE"
            log_success "FastAPI detenido (PID: $FASTAPI_PID)"
        else
            log_warning "FastAPI no está corriendo"
            rm -f "$FASTAPI_PID_FILE"
        fi
    else
        log_warning "FastAPI no está corriendo (no se encontró PID file)"
    fi

    # Fallback: si no hay PID file o quedó un worker huérfano, detener por puerto
    FASTAPI_PORT_PIDS=$(lsof -ti tcp:"$FASTAPI_PORT" -sTCP:LISTEN 2>/dev/null || true)
    if [ -n "$FASTAPI_PORT_PIDS" ]; then
        # shellcheck disable=SC2086
        kill $FASTAPI_PORT_PIDS 2>/dev/null || true
        log_success "FastAPI detenido por puerto $FASTAPI_PORT (PID(s): $FASTAPI_PORT_PIDS)"
    fi
    
    # Detener ngrok
    if [ -f "$NGROK_PID_FILE" ]; then
        NGROK_PID=$(cat "$NGROK_PID_FILE")
        if ps -p $NGROK_PID > /dev/null 2>&1; then
            kill $NGROK_PID 2>/dev/null || true
            rm -f "$NGROK_PID_FILE"
            log_success "ngrok detenido (PID: $NGROK_PID)"
        else
            log_warning "ngrok no está corriendo"
            rm -f "$NGROK_PID_FILE"
        fi
    else
        # Intentar matar ngrok por nombre
        if pgrep -x "ngrok" > /dev/null; then
            pkill -x ngrok
            log_success "ngrok detenido"
        else
            log_warning "ngrok no está corriendo"
        fi
    fi
    
    log_success "Todos los servicios detenidos"
    exit 0
}

cmd_status() {
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "📊 Estado de Servicios"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Estado FastAPI
    if [ -f "$FASTAPI_PID_FILE" ]; then
        FASTAPI_PID=$(cat "$FASTAPI_PID_FILE")
        if ps -p $FASTAPI_PID > /dev/null 2>&1; then
            log_success "FastAPI: ✅ Corriendo (PID: $FASTAPI_PID)"
            echo "           📍 http://localhost:$FASTAPI_PORT"
            echo "           📄 Log: $FASTAPI_LOG_FILE"
        else
            log_error "FastAPI: ❌ Proceso muerto (PID stale: $FASTAPI_PID)"
        fi
    else
        log_warning "FastAPI: ⚫ No está corriendo"
    fi
    
    # Estado ngrok
    if [ -f "$NGROK_PID_FILE" ]; then
        NGROK_PID=$(cat "$NGROK_PID_FILE")
        if ps -p $NGROK_PID > /dev/null 2>&1; then
            NGROK_PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | jq -r '.tunnels[0].public_url' 2>/dev/null || echo "ERROR")
            log_success "ngrok: ✅ Corriendo (PID: $NGROK_PID)"
            if [ "$NGROK_PUBLIC_URL" != "ERROR" ] && [ -n "$NGROK_PUBLIC_URL" ]; then
                echo "           🌐 $NGROK_PUBLIC_URL"
            fi
            echo "           🔧 Admin: http://localhost:4040"
            echo "           📄 Log: $NGROK_LOG_FILE"
        else
            log_error "ngrok: ❌ Proceso muerto (PID stale: $NGROK_PID)"
        fi
    elif pgrep -x "ngrok" > /dev/null; then
        log_warning "ngrok: ⚠️  Corriendo pero sin PID file (iniciado externamente)"
    else
        log_warning "ngrok: ⚫ No está corriendo"
    fi
    
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 0
}

cmd_logs() {
    if [ -f "$FASTAPI_LOG_FILE" ]; then
        log_info "Logs de FastAPI (Ctrl+C para salir):"
        echo ""
        tail -f "$FASTAPI_LOG_FILE"
    else
        log_error "No se encontró el archivo de logs: $FASTAPI_LOG_FILE"
        log_info "Asegurate de haber iniciado en modo daemon: ./run.sh --daemon"
        exit 1
    fi
}

# =============================================================================
# Cleanup al salir (Ctrl+C)
# =============================================================================

cleanup() {
    echo ""
    log_warning "Deteniendo servicios..."
    
    # Matar FastAPI (proceso en foreground)
    if [ -n "${FASTAPI_PID:-}" ]; then
        kill $FASTAPI_PID 2>/dev/null || true
        log_success "FastAPI detenido"
    fi
    
    # Matar ngrok si lo iniciamos nosotros
    if [ "${NGROK_STARTED_BY_US:-false}" = "true" ] && [ -f "$NGROK_PID_FILE" ]; then
        NGROK_PID=$(cat "$NGROK_PID_FILE")
        if ps -p $NGROK_PID > /dev/null 2>&1; then
            kill $NGROK_PID 2>/dev/null || true
            log_success "ngrok detenido (PID: $NGROK_PID)"
        fi
        rm -f "$NGROK_PID_FILE"
    fi
    
    log_info "Shutdown completo"
    exit 0
}

trap cleanup SIGINT SIGTERM

# =============================================================================
# Verificar entorno virtual
# =============================================================================

if [ ! -f "$VENV_PATH" ]; then
    log_error "Virtual environment no encontrado en: $VENV_PATH"
    echo "  Ejecuta: python3 -m venv venv"
    echo "  Luego:   source venv/bin/activate"
    echo "  Y:       pip install -r requirements.txt"
    exit 1
fi

log_info "Activando virtual environment..."
# shellcheck disable=SC1090
source "$VENV_PATH"
log_success "Virtual environment activado"

# =============================================================================
# Verificar run.py
# =============================================================================

if [ ! -f "run.py" ]; then
    log_error "No se encontró run.py en $SCRIPT_DIR"
    exit 1
fi

# =============================================================================
# Manejar flags
# =============================================================================

# Comandos especiales (no inician servicios)
case "${1:-}" in
    --stop)
        cmd_stop
        ;;
    --status)
        cmd_status
        ;;
    --logs)
        cmd_logs
        ;;
esac

# Flags de inicio
START_NGROK=true
DAEMON_MODE=false

for arg in "$@"; do
    case "$arg" in
        --mode)
            # Se procesa junto al próximo token en un segundo paso.
            ;;
        --mode=*)
            RUN_MODE="${arg#*=}"
            ;;
        --daemon|--background)
            DAEMON_MODE=true
            log_info "Modo: Daemon (background)"
            ;;
        --no-ngrok|--only-api)
            RUN_MODE="red-interna"
            ;;
    esac
done

# Procesar forma: --mode <valor>
for ((i=1; i<=$#; i++)); do
    if [ "${!i}" = "--mode" ]; then
        j=$((i+1))
        if [ $j -le $# ]; then
            RUN_MODE="${!j}"
        else
            log_error "Falta valor para --mode (usar: ngrok | red-interna | full)"
            exit 1
        fi
    fi
done

case "$RUN_MODE" in
    ngrok)
        START_NGROK=true
        EFFECTIVE_APP_HOST="127.0.0.1"
        ;;
    red-interna|red_interna|interna)
        START_NGROK=false
        EFFECTIVE_APP_HOST="0.0.0.0"
        ;;
    full)
        START_NGROK=true
        EFFECTIVE_APP_HOST="0.0.0.0"
        ;;
    *)
        log_error "Modo invalido: '$RUN_MODE'. Usar: ngrok | red-interna | full"
        exit 1
        ;;
esac

SERVER_LAN_IP="${SERVER_LAN_IP:-$(hostname -I | awk '{print $1}')}"
INTERNAL_ORIGIN="${INTERNAL_ORIGIN:-http://${SERVER_LAN_IP}:${FASTAPI_PORT}}"
NGROK_ORIGIN="https://${NGROK_URL}"
LOCAL_ORIGIN="http://127.0.0.1:${FASTAPI_PORT}"

case "$RUN_MODE" in
    ngrok)
        EFFECTIVE_CORS_ORIGINS="${LOCAL_ORIGIN},${NGROK_ORIGIN}"
        ;;
    red-interna|red_interna|interna)
        EFFECTIVE_CORS_ORIGINS="${LOCAL_ORIGIN},${INTERNAL_ORIGIN}"
        ;;
    full)
        EFFECTIVE_CORS_ORIGINS="${LOCAL_ORIGIN},${INTERNAL_ORIGIN},${NGROK_ORIGIN}"
        ;;
esac

log_info "Modo seleccionado: $RUN_MODE"
log_info "APP_HOST efectivo: $EFFECTIVE_APP_HOST"
log_info "CORS orígenes: $EFFECTIVE_CORS_ORIGINS"

# =============================================================================
# Iniciar ngrok (si es necesario)
# =============================================================================

NGROK_STARTED_BY_US=false

if [ "$START_NGROK" = "true" ]; then
    log_info "Verificando ngrok..."
    
    # Verificar si ngrok está instalado
    if ! command -v ngrok &> /dev/null; then
        log_error "ngrok no está instalado. Instala con:"
        echo "  sudo snap install ngrok"
        echo "  # o descarga desde https://ngrok.com/download"
        exit 1
    fi
    
    # Verificar si ngrok ya está corriendo
    if pgrep -x "ngrok" > /dev/null; then
        log_warning "ngrok ya está corriendo"
        
        # Verificar si tiene el dominio correcto
        CURRENT_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | jq -r '.tunnels[0].public_url' 2>/dev/null || echo "")
        
        if [[ "$CURRENT_URL" == *"$NGROK_URL"* ]]; then
            log_success "ngrok ya configurado con el dominio correcto: $CURRENT_URL"
        else
            log_warning "ngrok está corriendo pero con URL diferente: $CURRENT_URL"
            log_warning "Si quieres usar el dominio reservado, ejecuta: pkill ngrok && ./run.sh"
        fi
    else
        log_info "Iniciando ngrok con dominio reservado..."
        
        # Iniciar ngrok en background
        nohup ngrok http $FASTAPI_PORT --url=$NGROK_URL > "$NGROK_LOG_FILE" 2>&1 &
        NGROK_PID=$!
        echo $NGROK_PID > "$NGROK_PID_FILE"
        NGROK_STARTED_BY_US=true
        
        log_success "ngrok iniciado (PID: $NGROK_PID)"
        
        # Esperar a que ngrok esté listo
        log_info "Esperando a que ngrok esté listo..."
        for i in {1..10}; do
            if curl -s http://localhost:4040/api/tunnels > /dev/null 2>&1; then
                sleep 1  # Esperar un segundo más para que se estabilice
                break
            fi
            sleep 1
        done
        
        # Verificar URL pública
        NGROK_PUBLIC_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | jq -r '.tunnels[0].public_url' 2>/dev/null || echo "ERROR")
        
        if [ "$NGROK_PUBLIC_URL" = "ERROR" ] || [ -z "$NGROK_PUBLIC_URL" ] || [ "$NGROK_PUBLIC_URL" = "null" ]; then
            log_warning "No se pudo verificar la URL pública de ngrok"
            log_info "Verifica los logs en: $NGROK_LOG_FILE"
            log_info "O verifica en: http://localhost:4040"
        else
            log_success "ngrok online: $NGROK_PUBLIC_URL"
        fi
    fi
    
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "🌐 URL pública: https://$NGROK_URL"
    log_info "🔧 Admin UI:    http://localhost:4040"
    if [ "$DAEMON_MODE" = "true" ]; then
        log_info "📄 Logs:        $NGROK_LOG_FILE"
    fi
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# =============================================================================
# Iniciar FastAPI
# =============================================================================

log_info "Iniciando FastAPI en $EFFECTIVE_APP_HOST:$FASTAPI_PORT..."
echo ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🚀 FastAPI Backend"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "📍 Local:       http://127.0.0.1:$FASTAPI_PORT"
log_info "📍 Local API:   http://127.0.0.1:$FASTAPI_PORT/API/health"
if [ "$EFFECTIVE_APP_HOST" = "0.0.0.0" ]; then
    log_info "📍 LAN:         http://$SERVER_LAN_IP:$FASTAPI_PORT"
fi
log_info "📍 Frontend:    http://127.0.0.1:$FASTAPI_PORT/"

if [ "$START_NGROK" = "true" ]; then
    log_info "📍 Public:      https://$NGROK_URL"
    log_info "📍 Public API:  https://$NGROK_URL/API/health"
fi

if [ "$DAEMON_MODE" = "true" ]; then
    log_info "📄 Logs:        $FASTAPI_LOG_FILE"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "Comandos:"
    log_info "  ./run.sh --status    # Ver estado"
    log_info "  ./run.sh --logs      # Ver logs en tiempo real"
    log_info "  ./run.sh --stop      # Detener servicios"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Ejecutar FastAPI en background
    APP_HOST="$EFFECTIVE_APP_HOST" \
    APP_PORT="$FASTAPI_PORT" \
    FRONTEND_CORS_ORIGINS="$EFFECTIVE_CORS_ORIGINS" \
    FASTAPI_RELOAD=false nohup python run.py > "$FASTAPI_LOG_FILE" 2>&1 &
    FASTAPI_PID=$!
    echo $FASTAPI_PID > "$FASTAPI_PID_FILE"
    
    log_success "FastAPI iniciado en background (PID: $FASTAPI_PID)"
    log_info "Usa './run.sh --logs' para ver los logs"
    
else
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_warning "Presiona Ctrl+C para detener todos los servicios"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Ejecutar FastAPI en foreground (para ver logs)
    APP_HOST="$EFFECTIVE_APP_HOST" \
    APP_PORT="$FASTAPI_PORT" \
    FRONTEND_CORS_ORIGINS="$EFFECTIVE_CORS_ORIGINS" \
    python run.py &
    FASTAPI_PID=$!
    
    # Esperar a que FastAPI termine (o Ctrl+C)
    wait $FASTAPI_PID
fi
