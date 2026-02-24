#!/usr/bin/env bash

set -euo pipefail

echo "Diagnóstico dueño de :443"
echo "- fecha_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

echo "[ss -ltnp]"
ss -ltnp 2>/dev/null | grep ':443 ' || echo "  (sin datos de proceso en ss)"
echo

echo "[lsof -i :443]"
lsof -i :443 -sTCP:LISTEN -P -n 2>/dev/null || echo "  (sin datos o requiere permisos)"
echo

echo "[fuser -v 443/tcp]"
fuser -v 443/tcp 2>/dev/null || echo "  (sin datos o requiere permisos)"
echo

echo "Sugerencia:"
echo "- Si no aparece PID por permisos, ejecutar con sudo:"
echo "  sudo ss -ltnp | grep ':443 '"
echo "  sudo lsof -i :443 -sTCP:LISTEN -P -n"
