# Pruebas y cobertura

## Ejecutar tests
```powershell
python -m pytest -q
```

## Cobertura
```powershell
python -m pytest --cov=servidor --cov-report=term-missing
```

Si `--cov` da error, instalar:
```powershell
python -m pip install pytest-cov
```
