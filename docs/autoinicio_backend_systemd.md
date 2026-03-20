# Autoinicio Backend Interno (systemd)

## Objetivo
Levantar automaticamente el backend FastAPI en modo `red-interna` al iniciar la PC (Linux con `systemd`), sin ngrok.

## Decisiones aplicadas
- Modo fijo: `red-interna`.
- Arranque al boot: `WantedBy=multi-user.target`.
- Reinicio: `Restart=on-failure`.
- Puerto fijo por defecto: `8000`.
- Logs en `journald` (`journalctl`).
- Servicio corriendo con usuario no root.

## Requisitos
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Instalacion recomendada
Desde la raiz del repo:
```bash
./scripts/install_backend_autostart_systemd.sh
```

El instalador crea y habilita la unidad `calidad-fitba-backend.service` en:
- `/etc/systemd/system/calidad-fitba-backend.service`

## Verificacion
```bash
sudo systemctl status calidad-fitba-backend.service
curl -i http://127.0.0.1:8000/health
```

## Operacion diaria
```bash
sudo systemctl restart calidad-fitba-backend.service
sudo systemctl stop calidad-fitba-backend.service
sudo systemctl start calidad-fitba-backend.service
sudo journalctl -u calidad-fitba-backend.service -f
```

## Parametros opcionales de instalacion
```bash
./scripts/install_backend_autostart_systemd.sh \
  --service-name calidad-fitba-backend \
  --service-user agustin \
  --port 8000
```

Vista previa de la unidad (sin instalar):
```bash
./scripts/install_backend_autostart_systemd.sh --dry-run
```

## Desinstalacion manual
```bash
sudo systemctl disable --now calidad-fitba-backend.service
sudo rm -f /etc/systemd/system/calidad-fitba-backend.service
sudo systemctl daemon-reload
sudo systemctl reset-failed
```

## Nota tecnica
El script `scripts/start_backend_red_interna.sh` falla si el puerto configurado ya esta ocupado, para evitar que el backend cambie automaticamente a otro puerto y rompa integraciones.
