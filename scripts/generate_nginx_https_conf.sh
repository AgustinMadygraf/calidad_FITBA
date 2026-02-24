#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-api.madygraf.local}"
UPSTREAM_HOST="${UPSTREAM_HOST:-127.0.0.1}"
UPSTREAM_PORT="${UPSTREAM_PORT:-8000}"
TLS_CERT_PATH="${TLS_CERT_PATH:-/etc/ssl/certs/api-interna.crt}"
TLS_KEY_PATH="${TLS_KEY_PATH:-/etc/ssl/private/api-interna.key}"
OUT_FILE="${OUT_FILE:-/tmp/nginx_xubio_https.conf}"

cat > "$OUT_FILE" <<EOF
server {
    listen 80;
    server_name ${DOMAIN};
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ${DOMAIN};

    ssl_certificate     ${TLS_CERT_PATH};
    ssl_certificate_key ${TLS_KEY_PATH};
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers off;

    client_max_body_size 20m;

    location / {
        proxy_pass http://${UPSTREAM_HOST}:${UPSTREAM_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
EOF

echo "Archivo generado: $OUT_FILE"
echo "Resumen:"
echo "- domain: $DOMAIN"
echo "- upstream: http://${UPSTREAM_HOST}:${UPSTREAM_PORT}"
echo "- cert: $TLS_CERT_PATH"
echo "- key: $TLS_KEY_PATH"
