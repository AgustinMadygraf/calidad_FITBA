# Modelo Odoo-like (MVP literal)

## Tablas
- `res_partner`
  - `id`, `name`, `email`, `phone`
- `stock_picking`
  - `id`, `name` (UNIQUE), `partner_id`
- `stock_package_type`
  - `id`, `name`, `weight`
- `stock_quant_package`
  - `id`, `name` (UNIQUE), `package_type_id`, `shipping_weight`, `picking_id`

## Relaciones
- `stock_picking.partner_id` -> `res_partner.id`
- `stock_quant_package.package_type_id` -> `stock_package_type.id`
- `stock_quant_package.picking_id` -> `stock_picking.id`

## Notas
- Estructura literal a Odoo (nombres de tabla/campo).
- Alcance minimo viable para migracion futura.
