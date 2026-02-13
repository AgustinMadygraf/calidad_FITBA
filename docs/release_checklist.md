# Checklist de Release Tecnico

Proceso repetible antes de merge/release para evitar regresiones de contrato,
runtime y observabilidad.

## Ejecucion automatica (recomendada)

```bash
python scripts/release_check.py
```

El script valida, en este orden:
1. Contrato Swagger (`pytest -m contract`).
2. Cobertura minima por suite (`python scripts/run_coverage_suite.py all`).
3. Politicas de runtime (`tests/test_runtime_mode_policy.py` + `tests/test_runtime_policy_unit.py`).
4. Smoke HTTP de transporte (`tests/test_api_http_smoke.py`).
5. Logs y observabilidad (`tests/test_shared_logger.py` + `tests/test_observability_api.py`).

## Checklist manual (cuando aplique)

1. Verificar variables de entorno de destino (`IS_PROD`, OAuth2, DB, cache provider).
2. Confirmar feature flags esperadas para release (`XUBIO_CACHE_PROVIDER`, `XUBIO_GET_CACHE_ENABLED`).
3. Revisar que no haya endpoints fuera de contrato sin clasificar en relevamiento.
4. Confirmar doble confirmacion de BAJA en cliente para modo real.
