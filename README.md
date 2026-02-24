# FITBA Xubio-like (MVP)

Monorepo Python con:
- Backend FastAPI (API local Xubio-like).
- CLI interactiva de operación.

## Setup rápido
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Operación diaria
Servidor:
```bash
python run_server.py --mode red-interna
```

CLI:
```bash
python -m src.interface_adapter.controllers.terminal_cli
```

Script de ayuda para modo híbrido:
```bash
./scripts/setup_modo_hibrido.sh red-interna
```

Validación rápida:
```bash
curl -i http://127.0.0.1:8000/health
```

HTTPS interno (Apache en este host):
```bash
DOMAIN=api.madygraf.local ./scripts/generate_local_tls_cert.sh
DOMAIN=api.madygraf.local ./scripts/setup_apache_https_local.sh
```

## Comandos clave de CLI
- `MENU`
- `NETINFO` (alias `RED`)
- `ENTER <entity_type>`
- `GET <entity_type> <id>`
- `LIST <entity_type>`
- `BACK`
- `EXIT`

## Tests
```bash
pytest -q
```

## Documentación
- `docs/api_local.md`
- `docs/arquitectura.md`
- `docs/modo_hibrido_ngrok_red_interna.md`
- `docs/procedimiento_https_apache_dns_certificados.md`
- `docs/informe_cors_backend_frontend.md`
- `docs/informe_backend_a_frontend_cors_ngrok.md`
- `docs/release_checklist.md`
- `docs/swagger.json`
