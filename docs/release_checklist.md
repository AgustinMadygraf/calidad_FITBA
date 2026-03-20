# Checklist de Release Tecnico

Proceso repetible antes de merge/release para evitar regresiones de contrato y runtime.

## Ejecucion automatica recomendada
```bash
python scripts/release_check.py
```

## Checklist manual
1. Verificar variables de entorno de destino (OAuth2, DB, cache provider).
2. Confirmar configuraciones de cache esperadas (`XUBIO_CACHE_PROVIDER`, `XUBIO_GET_CACHE_ENABLED`).
3. Revisar que `docs/swagger.json` coincida con la version publicada.
4. Confirmar que no se hayan introducido endpoints mutadores en FastAPI.
