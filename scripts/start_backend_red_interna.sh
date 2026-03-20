#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/venv/bin/python}"
APP_HOST="${APP_HOST:-0.0.0.0}"
APP_PORT="${APP_PORT:-8000}"
FASTAPI_RELOAD="${FASTAPI_RELOAD:-false}"

is_port_busy() {
    local port="$1"

    if command -v lsof >/dev/null 2>&1; then
        if lsof -tiTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
            return 0
        fi
    fi

    if command -v ss >/dev/null 2>&1; then
        if ss -ltn "( sport = :$port )" 2>/dev/null | grep -q ":$port"; then
            return 0
        fi
    fi

    return 1
}

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "[backend-autostart] ERROR: no se encontro Python del venv en $PYTHON_BIN" >&2
    exit 1
fi

if is_port_busy "$APP_PORT"; then
    echo "[backend-autostart] ERROR: puerto $APP_PORT ocupado." >&2
    echo "[backend-autostart] Se aborta para evitar fallback automatico a otro puerto." >&2
    exit 1
fi

export APP_HOST
export APP_PORT
export FASTAPI_RELOAD
export PYTHONUNBUFFERED=1

exec "$PYTHON_BIN" run_server.py --mode red-interna
