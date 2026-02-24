#!/usr/bin/env bash

set -euo pipefail

PORT="${1:-8000}"

echo "=== Diagnóstico Red Interna ==="
echo "Puerto esperado: $PORT"
echo

echo "[1] IPs LAN detectadas:"
hostname -I || true
echo

echo "[2] Proceso escuchando en el puerto:"
ss -ltnp | grep ":$PORT" || echo "No hay listener en :$PORT"
echo

echo "[3] Estado firewall (si aplica):"
if command -v ufw >/dev/null 2>&1; then
  ufw status 2>/dev/null || echo "ufw requiere privilegios para mostrar estado completo."
else
  echo "ufw no instalado."
fi
echo

echo "[4] Prueba local al backend:"
curl -sS -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:$PORT/health" || true
echo

echo "[5] Siguiente prueba desde otra PC de fábrica:"
LAN_IP="$(hostname -I | awk '{print $1}')"
echo "curl -i http://${LAN_IP}:${PORT}/health"
echo

echo "[6] Si falla desde otra PC, revisar:"
echo "- Segmentación de red / VLAN."
echo "- Reglas de firewall del servidor."
echo "- Reglas de firewall perimetral/corporativo."
