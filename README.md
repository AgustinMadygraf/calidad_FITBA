# FITBA Xubio-like (MVP)

Monorepo Python con dos componentes:
- FastAPI (API local Xubio-like, solo lectura).
- CLI interactiva (solo lectura).

## Arquitectura (Clean Architecture)
- `src/entities/`: entidades y modelos de dominio.
- `src/use_cases/`: casos de uso.
- `src/interface_adapter/`: controllers, presenters y esquemas.
- `src/infrastructure/`: gateways HTTPX, FastAPI y memoria.
- `src/shared/`: helpers comunes (config/logger).

## API local (FastAPI)
- `GET /health`
- `GET /API/health`
- `GET /token/inspect`
- `GET /API/1.1/clienteBean`
- `GET /API/1.1/clienteBean/{id}`
- `GET /API/1.1/remitoVentaBean`
- `GET /API/1.1/remitoVentaBean/{id}`
- `GET /API/1.1/ProductoVentaBean`
- `GET /API/1.1/ProductoVentaBean/{id}`
- `GET /API/1.1/ProductoCompraBean`
- `GET /API/1.1/ProductoCompraBean/{id}`
- `GET /API/1.1/depositos`
- `GET /API/1.1/depositos/{id}`
- `GET /API/1.1/categoriaFiscal`
- `GET /API/1.1/categoriaFiscal/{id}`
- `GET /API/1.1/identificacionTributaria`
- `GET /API/1.1/identificacionTributaria/{id}`
- `GET /API/1.1/listaPrecioBean`
- `GET /API/1.1/listaPrecioBean/{id}`
- `GET /API/1.1/monedaBean`
- `GET /API/1.1/monedaBean/{id}`
- `GET /API/1.1/vendedorBean`
- `GET /API/1.1/vendedorBean/{id}`
- `GET /API/1.1/comprobanteVentaBean`
- `GET /API/1.1/comprobanteVentaBean/{id}`

Politica HTTP:
- Metodos no permitidos sobre rutas de recursos (`POST`, `PUT`, `PATCH`, `DELETE`) responden `405 Method Not Allowed`.

## Configuracion
Variables principales en `src/shared/config.py`:
- host/port (`APP_HOST`, `APP_PORT`)
- endpoint token (`XUBIO_TOKEN_ENDPOINT`)
- cache de lectura (`XUBIO_GET_CACHE_ENABLED`, `XUBIO_LIST_TTL_SECONDS`)
- frontend proxy dev (`FRONTEND_DEV_PROXY_ENABLED`, `FRONTEND_DEV_PROXY_URL`, `FRONTEND_DEV_PROXY_WS_ENABLED`)

Ya no existe `IS_PROD`.
Defaults:
- `APP_HOST=127.0.0.1`
- `APP_PORT=8000`

## Ejecutar servidor
```bash
uvicorn src.infrastructure.fastapi.api:app --reload --host 127.0.0.1 --port 8000
```

```bash
python run.py
```

Si el puerto configurado esta ocupado, `run.py` busca automaticamente el siguiente puerto disponible.
`run.py` también soporta modo:
```bash
python run.py --mode ngrok
python run.py --mode red-interna
python run.py --mode full
```

Entry point recomendado (`run.sh`) con selector de modo:
```bash
./run.sh                    # default: modo ngrok
./run.sh --mode ngrok       # solo ngrok
./run.sh --mode red-interna # solo LAN interna
./run.sh --mode full        # ngrok + LAN interna
```

Asistente de configuración automática (modo híbrido):
```bash
./scripts/setup_modo_hibrido.sh full
# o arranque automático:
START_SERVER=true ./scripts/setup_modo_hibrido.sh full
```

## Ejecutar CLI
```bash
python run_cli.py
```

Comandos disponibles:
- `MENU`
- `ENTER <entity_type>`
- `GET <entity_type> <id>`
- `LIST <entity_type>`
- `BACK`
- `EXIT`
- `DSP` (`LIST`/`GET` segun argumentos)

## Tests
```bash
pytest -q
```

## Documentacion adicional
- `docs/api_local.md`
- `docs/arquitectura.md`
- `docs/release_checklist.md`
- `docs/swagger.json`
