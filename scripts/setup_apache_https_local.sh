#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-api.madygraf.local}"
UPSTREAM_HOST="${UPSTREAM_HOST:-127.0.0.1}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8000}"
TLS_DIR="${TLS_DIR:-.runtime/tls}"
OUT_FILE="${OUT_FILE:-.runtime/apache/${DOMAIN}.conf}"

CERT_PATH="${TLS_DIR}/${DOMAIN}.crt"
KEY_PATH="${TLS_DIR}/${DOMAIN}.key"

if [[ ! -f "$CERT_PATH" || ! -f "$KEY_PATH" ]]; then
  echo "No existe cert/key para ${DOMAIN} en ${TLS_DIR}."
  echo "Generar primero:"
  echo "  DOMAIN=${DOMAIN} ./scripts/generate_local_tls_cert.sh"
  exit 1
fi

DOMAIN="$DOMAIN" \
UPSTREAM_HOST="$UPSTREAM_HOST" \
UPSTREAM_PORT="$UPSTREAM_PORT" \
TLS_CERT_PATH="$CERT_PATH" \
TLS_KEY_PATH="$KEY_PATH" \
OUT_FILE="$OUT_FILE" \
./scripts/generate_apache_https_vhost.sh

echo
echo "Próximos pasos (manuales, requieren root):"
echo "1) Habilitar módulos: sudo a2enmod ssl proxy proxy_http headers"
echo "2) Copiar conf a /etc/apache2/sites-available/${DOMAIN}.conf"
echo "3) Habilitar sitio: sudo a2ensite ${DOMAIN}.conf"
echo "4) Validar y recargar: sudo apache2ctl configtest && sudo systemctl reload apache2"
