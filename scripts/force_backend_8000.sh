#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PORT="${PORT:-8000}"
MODE="${MODE:-red-interna}"
WAIT_SECONDS="${WAIT_SECONDS:-8}"

log() {
  printf '[force_backend_8000] %s\n' "$1"
}

find_pids_on_port() {
  if command -v lsof >/dev/null 2>&1; then
    lsof -tiTCP:"$PORT" -sTCP:LISTEN 2>/dev/null || true
    return
  fi
  if command -v ss >/dev/null 2>&1; then
    ss -ltnp "sport = :$PORT" 2>/dev/null \
      | awk -F'pid=' 'NF>1{split($2,a,","); print a[1]}' \
      | sort -u || true
    return
  fi
  log "No se encontro ni lsof ni ss para detectar procesos en puerto $PORT"
}

kill_port_listeners() {
  local pids
  pids="$(find_pids_on_port | tr '\n' ' ' | xargs echo -n || true)"
  if [[ -z "${pids// }" ]]; then
    log "Puerto $PORT libre."
    return 0
  fi

  log "Matando procesos en puerto $PORT: $pids"
  # shellcheck disable=SC2086
  kill -TERM $pids 2>/dev/null || true

  local waited=0
  while [[ $waited -lt $WAIT_SECONDS ]]; do
    sleep 1
    waited=$((waited + 1))
    if [[ -z "$(find_pids_on_port | xargs echo -n || true)" ]]; then
      log "Puerto $PORT liberado con SIGTERM."
      return 0
    fi
  done

  pids="$(find_pids_on_port | tr '\n' ' ' | xargs echo -n || true)"
  if [[ -n "${pids// }" ]]; then
    log "Persisten procesos en puerto $PORT, aplicando SIGKILL: $pids"
    # shellcheck disable=SC2086
    kill -KILL $pids 2>/dev/null || true
  fi
}

kill_port_listeners

export APP_PORT="$PORT"
log "Iniciando backend en puerto $APP_PORT (mode=$MODE)"
exec python run_server.py --mode "$MODE"

