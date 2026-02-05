## Odoo-like (estructura literal, sin integracion)

### Decisiones acordadas
- Operacion: Delivery Orders (entregas).
- El peso se registra una sola vez.
- Estructura de datos literal a Odoo (nombres de tablas y campos).
- Minimo viable para migracion.
- Indices unicos en `stock_picking.name` y `stock_quant_package.name`.

### Tablas (MySQL)
- `res_partner`
  - `id`, `name`, `email`, `phone`
- `stock_picking`
  - `id`, `name`, `partner_id`
- `stock_package_type`
  - `id`, `name`, `weight`
- `stock_quant_package`
  - `id`, `name`, `package_type_id`, `shipping_weight`, `picking_id`

### Relacion principal
- El cliente se modela en `res_partner`.
- El Delivery Order es `stock_picking` y referencia a `res_partner`.
- El paquete es `stock_quant_package` y referencia a `stock_picking` y `stock_package_type`.

### API local (FastAPI)
- `POST /api/v1/res-partners`
- `POST /api/v1/stock-pickings`
- `POST /api/v1/stock-package-types`
- `POST /api/v1/stock-quant-packages`
- CRUD completo via `GET/PUT/DELETE` en cada recurso.

### Restricciones
- Sin campos custom.
- Peso total real en `shipping_weight` del paquete.
- Tara en `weight` del tipo de paquete.
