#!/usr/bin/env bash

set -euo pipefail

MODE="${1:-full}"
PORT="${BACKEND_PORT:-8000}"
NGROK_DOMAIN="${NGROK_DOMAIN:-confined-unexcused-garland.ngrok-free.dev}"
IP_HINT_PREFIX="${IP_HINT_PREFIX:-10.176.61.}"
START_SERVER="${START_SERVER:-false}"

if [[ "$MODE" != "ngrok" && "$MODE" != "red-interna" && "$MODE" != "full" ]]; then
  echo "ERROR: modo invalido '$MODE'. Usar: ngrok | red-interna | full"
  exit 1
fi

pick_internal_ip() {
  local ips
  ips="$(hostname -I 2>/dev/null || true)"
  if [[ -z "$ips" ]]; then
    return 1
  fi
  for ip in $ips; do
    if [[ "$ip" == ${IP_HINT_PREFIX}* ]]; then
      echo "$ip"
      return 0
    fi
  done
  for ip in $ips; do
    if [[ "$ip" != 127.* ]]; then
      echo "$ip"
      return 0
    fi
  done
  return 1
}

PORT_IN_USE=false
if ss -ltn "( sport = :$PORT )" | grep -q ":$PORT"; then
  PORT_IN_USE=true
fi

SERVER_IP="$(pick_internal_ip || true)"
if [[ -z "${SERVER_IP}" ]]; then
  SERVER_IP="10.176.61.<IP_SERVIDOR>"
fi

LOCAL_ORIGIN="http://127.0.0.1:${PORT}"
INTERNAL_ORIGIN="http://${SERVER_IP}:${PORT}"
NGROK_ORIGIN="https://${NGROK_DOMAIN}"

if [[ "$MODE" == "ngrok" ]]; then
  EFFECTIVE_HOST="127.0.0.1"
  CORS_ORIGINS="${LOCAL_ORIGIN},${NGROK_ORIGIN}"
elif [[ "$MODE" == "red-interna" ]]; then
  EFFECTIVE_HOST="0.0.0.0"
  CORS_ORIGINS="${LOCAL_ORIGIN},${INTERNAL_ORIGIN}"
else
  EFFECTIVE_HOST="0.0.0.0"
  CORS_ORIGINS="${LOCAL_ORIGIN},${INTERNAL_ORIGIN},${NGROK_ORIGIN}"
fi

echo "=== Setup Modo Híbrido ==="
echo "Modo:              $MODE"
echo "APP_HOST:          $EFFECTIVE_HOST"
echo "APP_PORT:          $PORT"
echo "SERVER_IP:         $SERVER_IP"
echo "FRONTEND_CORS_ORIGINS:"
echo "  $CORS_ORIGINS"
if [[ "$PORT_IN_USE" == true ]]; then
  echo "WARNING: Puerto $PORT ocupado. run.py aplicará fallback automático."
fi
echo

echo "Export sugerido:"
echo "export APP_HOST=\"$EFFECTIVE_HOST\""
echo "export APP_PORT=\"$PORT\""
echo "export FRONTEND_CORS_ORIGINS=\"$CORS_ORIGINS\""
echo "export NGROK_DOMAIN=\"$NGROK_DOMAIN\""
echo

echo "Smokes recomendados:"
echo "curl -i \"$LOCAL_ORIGIN/health\""
if [[ "$MODE" != "ngrok" ]]; then
  echo "curl -i \"$INTERNAL_ORIGIN/health\""
fi
if [[ "$MODE" == "ngrok" || "$MODE" == "full" ]]; then
  echo "curl -i \"$NGROK_ORIGIN/health\""
fi
echo

if [[ "$START_SERVER" == "true" ]]; then
  echo "Iniciando backend..."
  export APP_HOST="$EFFECTIVE_HOST"
  export APP_PORT="$PORT"
  export FRONTEND_CORS_ORIGINS="$CORS_ORIGINS"
  python run.py --mode "$MODE"
fi
