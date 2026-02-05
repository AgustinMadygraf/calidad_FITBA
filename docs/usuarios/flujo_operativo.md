# Flujo operativo (entregas)

## Objetivo
Registrar el peso total de cajas con estructura Odoo-like para migracion futura,
manteniendo una trazabilidad basica entre cliente, entrega y paquete.

## Alcance
- Se registra **peso total** en `stock_quant_package.shipping_weight`.
- La **tara** se registra en `stock_package_type.weight`.
- El peso se registra **una sola vez** por paquete.

## Conceptos
- **Cliente**: se modela en `res.partner`.
- **Entrega**: se modela en `stock.picking` y referencia al cliente.
- **Tipo de caja**: se modela en `stock.package.type` con la tara.
- **Paquete**: se modela en `stock.quant.package` con el peso total.

## Pre-chequeos (antes de operar)
- API levantada (`/health` devuelve `ok`).
- Base de datos creada y conectada.
- Contar con referencias unicas para:
  - `stock_picking.name`
  - `stock_quant_package.name`

## Secuencia recomendada (paso a paso)
1. **Alta de cliente** (`res.partner`).
   Datos minimos:
   - `name` (obligatorio)
   - `email` (opcional)
   - `phone` (opcional)

2. **Alta de entrega** (`stock.picking`).
   Datos minimos:
   - `name` (obligatorio, unico)
   - `partner_id` (obligatorio, debe existir)

3. **Alta de tipo de caja** (`stock.package.type`).
   Datos minimos:
   - `name` (obligatorio)
   - `weight` (tara, >= 0)

4. **Alta de paquete** (`stock.quant.package`).
   Datos minimos:
   - `name` (obligatorio, unico)
   - `package_type_id` (obligatorio, debe existir)
   - `picking_id` (obligatorio, debe existir)
   - `shipping_weight` (peso total, >= 0)

## Flujo en la CLI (paso a paso)
1. Menu principal -> `1` Partners -> Alta.
2. Menu principal -> `2` Pickings -> Alta.
3. Menu principal -> `3` Package Types -> Alta.
4. Menu principal -> `4` Packages -> Alta.

## Ejemplo completo
1. Crear cliente:
   - `name`: Cliente A
   - `email`: cliente@empresa.com
2. Crear entrega:
   - `name`: OUT/0001
   - `partner_id`: (ID del Cliente A)
3. Crear tipo de caja:
   - `name`: Caja Mediana
   - `weight`: 0.50
4. Crear paquete:
   - `name`: PACK0001
   - `package_type_id`: (ID de Caja Mediana)
   - `picking_id`: (ID de OUT/0001)
   - `shipping_weight`: 10.25

## Validaciones y reglas
- `name` no puede estar vacio.
- `weight` y `shipping_weight` no pueden ser negativos.
- `partner_id`, `package_type_id`, `picking_id` deben existir.
- Referencias `name` deben ser unicas donde aplica.

## Errores comunes y como resolver
- **422 Unprocessable Entity**: payload invalido (campo requerido ausente o tipo incorrecto).
  - Solucion: revisar campos obligatorios y tipos numericos.
- **400 Bad Request**: validacion de dominio (nombre vacio, peso negativo).
  - Solucion: corregir dato segun regla.
- **404 Not Found**: ID inexistente.
  - Solucion: confirmar ID en listados.
- **409 Conflict** (si se implementa): referencia duplicada.
  - Solucion: usar un `name` unico.

## Controles recomendados
- Registrar un formato estandar para referencias:
  - Pickings: `OUT/0001`, `OUT/0002`.
  - Paquetes: `PACK0001`, `PACK0002`.
- Si se usa balanza, definir el momento exacto de captura del peso y un unico registro.

## Campos clave (resumen)
- `res_partner.name`: cliente.
- `stock_picking.name`: referencia de entrega.
- `stock_package_type.weight`: tara.
- `stock_quant_package.shipping_weight`: peso total.
