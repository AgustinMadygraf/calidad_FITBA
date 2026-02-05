# To Do (pendientes)

## Decisiones funcionales
- Definir identificador de operacion para balanza de materia prima (equivalente a `stock_picking.name`).
- Definir si el proveedor se registra en `res_partner` y con que datos minimos.
- Confirmar si el peso se registra una sola vez tambien para bobinas.
- Definir si hay tara por cono de 3 pulgadas y si se modela en `stock_package_type.weight`.
- Definir si el peso que llega de la balanza es bruto o neto y como se guarda en `stock_quant_package.shipping_weight`.

## Modelado Odoo-like (sin campos custom)
- Confirmar si la bobina se modela como `stock_quant_package` (unidad de conteo = bobina).
- Definir convencion de `stock_picking.name` para entradas de materia prima (sin campo "tipo").
- Definir convencion de `stock_quant_package.name` para bobinas.

## Integracion y datos
- Especificar formato de datos que entregara el sistema de ingesta automatica.
- Confirmar si se necesita timestamp u operador (no hay campos en el modelo actual).
- Definir validaciones de dominio (rango de pesos, tolerancias, unidades).

## Documentacion
- Agregar un flujo operativo para materia prima en `docs/usuarios/flujo_operativo.md`.
- Agregar ejemplos de uso de la CLI para bobinas en `docs/usuarios/uso_cli.md`.

## Relevamiento de requisitos (preguntas)
- Identificador de operacion para entrada de bobinas (remito, lote, ticket, orden u otro).
- El peso capturado es bruto o neto.
- Si se registra el cono de 3 pulgadas como tara en `stock_package_type.weight`.
- Si la bobina mapea 1 a 1 con `stock_quant_package`.
- Si hay proveedor identificado y cuales son los datos minimos en `res_partner`.
