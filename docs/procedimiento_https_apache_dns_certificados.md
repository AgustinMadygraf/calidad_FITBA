# Procedimiento HTTPS Interno (Apache + DNS/Hosts + Certificados)

Fecha: 2026-02-24  
Objetivo: publicar API interna en `https://api.madygraf.local` usando Apache en la misma máquina (`10.176.61.33`).

## Estado actual confirmado
- `apache2` ocupa `:443`.
- Backend FastAPI responde en `127.0.0.1:8000`.
- Cert y key locales disponibles en `.runtime/tls/`.
- VHost Apache generado en `.runtime/apache/api.madygraf.local.conf`.

## Paso 1: DNS interno (recomendado) o hosts
Opción A - DNS corporativo:
- Crear registro `A`: `api.madygraf.local -> 10.176.61.33`

Opción B - archivo `hosts` por cliente:
- Linux/macOS:
```bash
echo "10.176.61.33 api.madygraf.local" | sudo tee -a /etc/hosts
```
- Windows (admin):
  - editar `C:\Windows\System32\drivers\etc\hosts`
  - agregar: `10.176.61.33 api.madygraf.local`

Validación:
```bash
nslookup api.madygraf.local || getent hosts api.madygraf.local
ping -c 1 api.madygraf.local
```

## Paso 2: Certificado
Alternativas:
1. Self-signed local (rápido, usar solo para pruebas internas temporales).
2. Certificado emitido por CA corporativa (requerido para producción interna).

Generación local:
```bash
DOMAIN=api.madygraf.local ./scripts/generate_local_tls_cert.sh
```

## Paso 3: Generar/ajustar vhost Apache
```bash
DOMAIN=api.madygraf.local ./scripts/setup_apache_https_local.sh
```

Archivo generado:
- `.runtime/apache/api.madygraf.local.conf`

## Paso 4: Aplicar en Apache (requiere sudo)
```bash
sudo a2enmod ssl proxy proxy_http headers
sudo cp .runtime/apache/api.madygraf.local.conf /etc/apache2/sites-available/api.madygraf.local.conf
sudo a2ensite api.madygraf.local.conf
sudo apache2ctl configtest
sudo systemctl reload apache2
```

## Paso 5: Validación end-to-end
Servidor:
```bash
curl -ik https://api.madygraf.local/health
```

Cliente LAN:
```bash
curl -ik https://api.madygraf.local/health
```

## Criterio de cierre
1. `https://api.madygraf.local/health` responde `200`.
2. Frontend consume `https://api.madygraf.local/API/...` (o mismo origen HTTPS).
3. Sin bloqueos CORS/mixed-content en navegador.
4. Certificado confiable en clientes (CA corporativa en producción).

## Política acordada
- Producción: CA corporativa (obligatorio).
- Self-signed local: permitido solo para pruebas/puesta a punto.
