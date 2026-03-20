#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-api.madygraf.local}"
UPSTREAM_URL="${UPSTREAM_URL:-http://127.0.0.1:8000/health}"

echo "Checklist HTTPS readiness"
echo "- fecha_utc: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

echo "[1] Puerto 443 en escucha (host local)"
if ss -ltn | grep -q ':443 '; then
  echo "  - resultado: SI (hay proceso escuchando)"
else
  echo "  - resultado: NO (libre)"
fi

echo "[2] Apache instalado"
if command -v apache2 >/dev/null 2>&1; then
  echo "  - resultado: SI ($(apache2 -v | head -n1))"
else
  echo "  - resultado: NO"
fi

echo "[3] Upstream FastAPI"
if curl -fsS --max-time 3 "$UPSTREAM_URL" >/dev/null 2>&1; then
  echo "  - resultado: SI ($UPSTREAM_URL responde)"
else
  echo "  - resultado: NO ($UPSTREAM_URL no responde)"
fi

echo "[4] DNS interno"
if getent hosts "$DOMAIN" >/dev/null 2>&1; then
  echo "  - resultado: SI ($(getent hosts "$DOMAIN" | head -n1))"
else
  echo "  - resultado: NO (sin resolucion para $DOMAIN)"
fi

echo
echo "Siguiente accion sugerida:"
echo "- Si [1]=SI y no sabes el dueño de 443: identificar servicio antes de cambiar."
echo "- Generar cert local: ./scripts/generate_local_tls_cert.sh"
echo "- Generar conf Apache: ./scripts/setup_apache_https_local.sh"
