# Modo Red Interna + Remoto (estado vigente)

Fecha de actualización: 2026-02-24

## Objetivo
- Operar backend en LAN interna (`10.176.61.33:8000`).
- Exponer HTTPS interno en `api.madygraf.local` con Apache (`443 -> 127.0.0.1:8000`).
- Mantener opción remota (ngrok) separada del uso LAN.

## Estado confirmado
- Backend OK en `http://10.176.61.33:8000`.
- Apache ocupa `443` en esta máquina.
- HTTPS servidor validado:
  - `curl -ik https://api.madygraf.local/health` => `200 OK` (con hosts local).

## Decisiones cerradas
- Reverse proxy oficial en este host: `apache2`.
- Nginx: alternativa genérica, no camino recomendado aquí.
- Certificados:
  - Producción: CA corporativa (obligatorio).
  - Self-signed local: solo pruebas temporales.

## Comandos operativos
Arranque backend:
```bash
python run.py --mode red-interna
```

Diagnóstico:
```bash
./scripts/check_ip_stability.sh
./scripts/check_https_readiness.sh
./scripts/detect_443_owner.sh
```

Preparación HTTPS local (artefactos):
```bash
DOMAIN=api.madygraf.local ./scripts/generate_local_tls_cert.sh
DOMAIN=api.madygraf.local ./scripts/setup_apache_https_local.sh
```

Aplicación Apache (sudo):
```bash
sudo a2enmod ssl proxy proxy_http headers
sudo cp .runtime/apache/api.madygraf.local.conf /etc/apache2/sites-available/api.madygraf.local.conf
sudo a2ensite api.madygraf.local.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## Pendientes para cierre productivo
1. DNS interno:
- `api.madygraf.local -> 10.176.61.33`
2. Certificado CA corporativa en Apache.
3. Frontend consumiendo `https://api.madygraf.local/API/...` (o same-origin HTTPS).
4. Validación desde equipo LAN cliente (no solo servidor).
