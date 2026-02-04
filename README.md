# CRUD Contactos (Python 3.11+)

Arquitectura Clean Architecture + DDD, CLI estilo AS/400 con `rich`.

## Setup

1. Crear entorno virtual e instalar dependencias

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional `.env`)

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=secret
DB_NAME=contacts
```

3. Crear esquema en MySQL

```bash
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME < scripts/schema.sql
```

## Ejecutar CLI

```bash
python -m app
```

## Tests

```bash
pytest -q
```

Para tests de integración:

```bash
pytest -q -m integration
```
