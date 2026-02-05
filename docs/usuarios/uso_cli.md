# Uso de la CLI (estilo AS400)

## Requisitos
- API ejecutando en `http://localhost:8000` o con `NGROK_URL` configurado.
- Variables en `.env` (ver `README.md`).

## Inicio
```powershell
python -m cliente.app
```

## Menu principal
- `1` Partners (res.partner)
- `2` Pickings (stock.picking)
- `3` Package Types (stock.package.type)
- `4` Packages (stock.quant.package)

## Flujo recomendado (entregas)
1. Crear `Partner`.
2. Crear `Picking` con `partner_id`.
3. Crear `Package Type` con tara (peso de caja).
4. Crear `Package` con referencia, tipo, picking y peso total.

## Atajos
- `ESC`: cancelar
- `0`: volver/salir
