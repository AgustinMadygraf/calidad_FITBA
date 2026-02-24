#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-api.madygraf.local}"
UPSTREAM_HOST="${UPSTREAM_HOST:-127.0.0.1}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8000}"
TLS_CERT_PATH="${TLS_CERT_PATH:-.runtime/tls/api.madygraf.local.crt}"
TLS_KEY_PATH="${TLS_KEY_PATH:-.runtime/tls/api.madygraf.local.key}"
OUT_FILE="${OUT_FILE:-.runtime/apache/${DOMAIN}.conf}"

mkdir -p "$(dirname "$OUT_FILE")"

cat > "$OUT_FILE" <<EOF
<VirtualHost *:80>
    ServerName ${DOMAIN}
    Redirect permanent / https://${DOMAIN}/
</VirtualHost>

<IfModule mod_ssl.c>
<VirtualHost *:443>
    ServerName ${DOMAIN}

    SSLEngine on
    SSLCertificateFile ${TLS_CERT_PATH}
    SSLCertificateKeyFile ${TLS_KEY_PATH}

    ProxyPreserveHost On
    RequestHeader set X-Forwarded-Proto "https"
    ProxyPass / http://${UPSTREAM_HOST}:${UPSTREAM_PORT}/
    ProxyPassReverse / http://${UPSTREAM_HOST}:${UPSTREAM_PORT}/

    ErrorLog \${APACHE_LOG_DIR}/${DOMAIN}_error.log
    CustomLog \${APACHE_LOG_DIR}/${DOMAIN}_access.log combined
</VirtualHost>
</IfModule>
EOF

echo "Archivo generado: $OUT_FILE"
echo "Resumen:"
echo "- domain: $DOMAIN"
echo "- upstream: http://${UPSTREAM_HOST}:${UPSTREAM_PORT}"
echo "- cert: $TLS_CERT_PATH"
echo "- key: $TLS_KEY_PATH"
