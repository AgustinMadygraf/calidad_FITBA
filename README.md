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

Autoinicio Linux (systemd, solo backend interno):
```bash
./scripts/install_backend_autostart_systemd.sh
```

Script de ayuda para modo híbrido:
```bash
./scripts/setup_modo_hibrido.sh red-interna
```

Validación rápida:
```bash
curl -i http://127.0.0.1:8000/health
```

Forzar backend en `8000` (mata cualquier proceso ocupando el puerto y arranca FastAPI):
```bash
./scripts/force_backend_8000.sh
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

## Contrato ComprobanteVenta
- Endpoint: `GET /API/1.1/comprobanteVentaBean/{id}` y `GET /API/1.1/comprobanteVentaBean`.
- La salida se normaliza para cumplir el contrato Xubio (golden contract) con keys exactas, incluyendo defaults `0`, `false`, `\"\"`, `null` y arrays vacios `[]` cuando faltan datos en origen.
- `CAE` se expone solo en mayusculas (no se devuelve `cae` ni otros aliases no contractuales).
- `provincia` se serializa con shape `{provincia_id, codigo, nombre, pais}`.

## Documentación
- `docs/api_local.md`
- `docs/arquitectura.md`
- `docs/modo_hibrido_ngrok_red_interna.md`
- `docs/procedimiento_crear_api_madygraf_local.md`
- `docs/procedimiento_https_apache_dns_certificados.md`
- `docs/autoinicio_backend_systemd.md`
- `docs/informe_backend_a_frontend_cors_ngrok.md`
- `docs/release_checklist.md`
- `docs/swagger.json`
