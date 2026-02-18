#!/usr/bin/env bash

# =============================================================================
# run.sh - Inicia ngrok + FastAPI para el entorno de desarrollo
# =============================================================================
# Uso:
#   ./run.sh              # Inicia todo (ngrok + FastAPI)
#   ./run.sh --no-ngrok   # Solo FastAPI (útil si ngrok ya está corriendo)
#   ./run.sh --only-api   # Alias para --no-ngrok
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
NGROK_PID_FILE="${NGROK_PID_FILE:-/tmp/ngrok_calidad_fitba.pid}"
VENV_PATH="${VENV_PATH:-$SCRIPT_DIR/venv/bin/activate}"

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

START_NGROK=true
if [ "${1:-}" = "--no-ngrok" ] || [ "${1:-}" = "--only-api" ]; then
    START_NGROK=false
    log_info "Modo: Solo FastAPI (ngrok no se iniciará)"
fi

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
        nohup ngrok http $FASTAPI_PORT --url=$NGROK_URL > /tmp/ngrok_output.log 2>&1 &
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
            log_info "Verifica los logs en: /tmp/ngrok_output.log"
            log_info "O verifica en: http://localhost:4040"
        else
            log_success "ngrok online: $NGROK_PUBLIC_URL"
        fi
    fi
    
    echo ""
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_info "🌐 URL pública: https://$NGROK_URL"
    log_info "🔧 Admin UI:    http://localhost:4040"
    log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# =============================================================================
# Iniciar FastAPI
# =============================================================================

log_info "Iniciando FastAPI en localhost:$FASTAPI_PORT..."
echo ""
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "🚀 FastAPI Backend"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_info "📍 Local:       http://localhost:$FASTAPI_PORT"
log_info "📍 Local API:   http://localhost:$FASTAPI_PORT/API/health"
log_info "📍 Frontend:    http://localhost:$FASTAPI_PORT/"

if [ "$START_NGROK" = "true" ]; then
    log_info "📍 Public:      https://$NGROK_URL"
    log_info "📍 Public API:  https://$NGROK_URL/API/health"
fi

log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_warning "Presiona Ctrl+C para detener todos los servicios"
log_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Ejecutar FastAPI en foreground (para ver logs)
python run.py "$@" &
FASTAPI_PID=$!

# Esperar a que FastAPI termine (o Ctrl+C)
wait $FASTAPI_PID
