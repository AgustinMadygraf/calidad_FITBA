# Procedimiento: crear `api.madygraf.local`

## Objetivo
Crear y validar el nombre interno `api.madygraf.local` para que resuelva al servidor backend.

## Datos objetivo
- FQDN: `api.madygraf.local`
- IP servidor: `10.176.61.33`

## Opción recomendada: DNS interno corporativo
1. Crear registro `A`:
- `api.madygraf.local -> 10.176.61.33`
- TTL sugerido inicial: `300` segundos.

2. Validar resolución:
```bash
nslookup api.madygraf.local
dig +short api.madygraf.local
```

Esperado:
- `10.176.61.33`

## Opción temporal: hosts local por equipo
Linux/macOS:
```bash
echo "10.176.61.33 api.madygraf.local" | sudo tee -a /etc/hosts
```

Windows (Administrador):
- Editar `C:\Windows\System32\drivers\etc\hosts`
- Agregar:
```txt
10.176.61.33 api.madygraf.local
```

## Verificación funcional final
```bash
curl -ik https://api.madygraf.local/health
```

Esperado:
- `HTTP/1.1 200`
- `{"status":"ok"}`

## Nota operativa
- En producción debe usarse DNS interno (no hosts manual).
