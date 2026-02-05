# Build .exe del cliente (CLI)

Esta guia describe como generar un ejecutable `.exe` del cliente CLI con el flujo actual
(hardcodeando el ngrok antes del build).

## Requisitos
- Windows.
- Entorno virtual activo.
- `pyinstaller` instalado.

Instalar PyInstaller (una sola vez):

```bash
pip install pyinstaller
```

## Pasos
1) Hardcodear el ngrok antes del build

Editar `cliente/infrastructure/api_client.py` y setear el valor de
`HARD_CODED_NGROK_URL` con el subdominio de ngrok actual (sin `https://`):

```python
HARD_CODED_NGROK_URL = "tu-subdominio.ngrok-free.app"
```

2) Generar el ejecutable

Desde la raiz del proyecto:

```bash
pyinstaller --onefile --name cliente_cli cliente/app/__main__.py
```

El `.exe` queda en `dist/cliente_cli.exe`.

3) Revertir el hardcode del ngrok

Volver a dejar el valor de `HARD_CODED_NGROK_URL` como estaba antes del build
para que el flujo normal siga leyendo `NGROK_URL` del entorno.

## Notas
- El servidor debe estar corriendo o accesible via ngrok para usar el `.exe`.
- Si el antivirus bloquea el `.exe`, agregar una excepcion para `dist/cliente_cli.exe`.
