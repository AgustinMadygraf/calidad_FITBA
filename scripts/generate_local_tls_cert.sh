#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-api.madygraf.local}"
TLS_DIR="${TLS_DIR:-.runtime/tls}"
DAYS="${DAYS:-825}"

mkdir -p "$TLS_DIR"

KEY_PATH="$TLS_DIR/${DOMAIN}.key"
CRT_PATH="$TLS_DIR/${DOMAIN}.crt"

openssl req -x509 -nodes -newkey rsa:2048 \
  -keyout "$KEY_PATH" \
  -out "$CRT_PATH" \
  -days "$DAYS" \
  -subj "/CN=${DOMAIN}" \
  -addext "subjectAltName=DNS:${DOMAIN}" >/dev/null 2>&1

chmod 600 "$KEY_PATH"
chmod 644 "$CRT_PATH"

echo "Certificado generado:"
echo "- domain: $DOMAIN"
echo "- key: $KEY_PATH"
echo "- crt: $CRT_PATH"
echo
echo "Nota:"
echo "- Este certificado es local/self-signed."
echo "- En clientes LAN, confiar el certificado o usar CA corporativa."
