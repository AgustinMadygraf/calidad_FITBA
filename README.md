# CRUD Odoo-like (Python 3.11+)

Proyecto dividido en dos carpetas principales:
- `servidor/`: Backend FastAPI + Clean Architecture + MySQL.
- `cliente/`: CLI estilo AS/400 que consume la API.

## Setup

1. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
```

Activación según shell:

PowerShell (Windows):

```powershell
.\venv\Scripts\Activate.ps1
```

CMD (Windows):

```cmd
venv\Scripts\activate.bat
```

Git Bash / WSL / Linux / macOS:

```bash
source venv/bin/activate
```

Luego instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional `.env`)

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secret
DB_NAME=odoo_like
NGROK_URL=your-subdomain.ngrok-free.app
API_PORT=8000
```

## Servidor (FastAPI)

El servidor crea el esquema automáticamente al iniciar (si no existe).

```bash
python -m servidor.app
```

Health check:

```bash
curl http://localhost:8000/health
```

## Túnel ngrok

```bash
python run_ngrok_tunnel.py
```

## Cliente (CLI)

```bash
python -m cliente.app
```

## Tests

```bash
pytest -q
```

Para tests de integración (MySQL):

```bash
pytest -q -m integration
```

