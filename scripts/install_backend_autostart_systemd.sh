#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="${SERVICE_NAME:-calidad-fitba-backend.service}"
SERVICE_USER="${SERVICE_USER:-$(id -un)}"
APP_PORT="${APP_PORT:-8000}"
DRY_RUN=false

usage() {
    cat <<'EOF'
Uso:
  ./scripts/install_backend_autostart_systemd.sh [opciones]

Opciones:
  --service-name <nombre>  Nombre de la unidad (default: calidad-fitba-backend.service)
  --service-user <usuario> Usuario Linux que ejecuta el backend (default: usuario actual)
  --port <puerto>          Puerto fijo para FastAPI (default: 8000)
  --dry-run                Imprime la unidad y no instala nada
  -h, --help               Muestra esta ayuda
EOF
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --service-name)
            SERVICE_NAME="${2:-}"
            shift 2
            ;;
        --service-user)
            SERVICE_USER="${2:-}"
            shift 2
            ;;
        --port)
            APP_PORT="${2:-}"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: opcion no reconocida: $1" >&2
            usage
            exit 1
            ;;
    esac
done

if [[ "$SERVICE_NAME" != *.service ]]; then
    SERVICE_NAME="${SERVICE_NAME}.service"
fi

if ! [[ "$APP_PORT" =~ ^[0-9]+$ ]] || ((APP_PORT < 1 || APP_PORT > 65535)); then
    echo "ERROR: --port debe estar entre 1 y 65535" >&2
    exit 1
fi

if ! id "$SERVICE_USER" >/dev/null 2>&1; then
    echo "ERROR: el usuario '$SERVICE_USER' no existe en el sistema" >&2
    exit 1
fi

if ! command -v systemctl >/dev/null 2>&1; then
    echo "ERROR: systemctl no disponible. Este instalador requiere Linux con systemd." >&2
    exit 1
fi

START_SCRIPT="$ROOT_DIR/scripts/start_backend_red_interna.sh"
if [[ ! -x "$START_SCRIPT" ]]; then
    echo "ERROR: script de arranque no ejecutable: $START_SCRIPT" >&2
    exit 1
fi

if [[ ! -x "$ROOT_DIR/venv/bin/python" ]]; then
    echo "ERROR: no se encontro $ROOT_DIR/venv/bin/python" >&2
    echo "Sugerencia: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt" >&2
    exit 1
fi

run_privileged() {
    if [[ $EUID -eq 0 ]]; then
        "$@"
        return
    fi
    if ! command -v sudo >/dev/null 2>&1; then
        echo "ERROR: sudo no disponible y no se ejecuto como root." >&2
        exit 1
    fi
    sudo "$@"
}

build_unit() {
    cat <<EOF
[Unit]
Description=FITBA Backend FastAPI (red-interna)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${SERVICE_USER}
WorkingDirectory=${ROOT_DIR}
EnvironmentFile=-${ROOT_DIR}/.env
Environment=APP_HOST=0.0.0.0
Environment=APP_PORT=${APP_PORT}
Environment=FASTAPI_RELOAD=false
Environment=PYTHONUNBUFFERED=1
ExecStart=${START_SCRIPT}
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=calidad-fitba-backend
KillSignal=SIGTERM
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF
}

if [[ "$DRY_RUN" == "true" ]]; then
    build_unit
    exit 0
fi

UNIT_PATH="/etc/systemd/system/${SERVICE_NAME}"
TMP_FILE="$(mktemp)"
build_unit > "$TMP_FILE"

run_privileged install -m 0644 "$TMP_FILE" "$UNIT_PATH"
rm -f "$TMP_FILE"

run_privileged systemctl daemon-reload
run_privileged systemctl enable --now "$SERVICE_NAME"

echo "Unidad instalada: $UNIT_PATH"
echo "Servicio habilitado y levantado: $SERVICE_NAME"
echo "Comandos utiles:"
echo "  sudo systemctl status $SERVICE_NAME"
echo "  sudo journalctl -u $SERVICE_NAME -f"
echo "  sudo systemctl restart $SERVICE_NAME"
