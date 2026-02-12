# Relevamiento de Endpoints Xubio (Swagger)

Fecha de relevamiento: **2026-02-12**  
Fuente oficial: `https://xubio.com/API/documentation/index.html`  
Swagger usado: `https://xubio.com/API/1.1/swagger.json`

## Resumen ejecutivo
- Endpoints oficiales relevados en Swagger: **62 paths**
- Operaciones oficiales relevadas (GET/POST/PUT/PATCH/DELETE): **105**
- Operaciones cubiertas por la API local (matching contra Swagger): **28**
- Operaciones pendientes respecto de Swagger: **77**
- Operaciones locales fuera de Swagger (extensiones formales): **11**

## Endpoints relevados y cubiertos (oficial vs local)
- `/API/1.1/ProductoCompraBean`: cubierto=`[GET]`
- `/API/1.1/ProductoVentaBean`: cubierto=`[GET, POST]`
- `/API/1.1/ProductoVentaBean/{id}`: cubierto=`[DELETE, PATCH, PUT]` | local-extra=`[GET]`
- `/API/1.1/categoriaFiscal`: cubierto=`[GET]`
- `/API/1.1/clienteBean`: cubierto=`[GET, POST]`
- `/API/1.1/clienteBean/{id}`: cubierto=`[DELETE, GET, PUT]` | local-extra=`[PATCH]`
- `/API/1.1/comprobanteVentaBean`: cubierto=`[GET]`
- `/API/1.1/comprobanteVentaBean/{id}`: cubierto=`[GET]`
- `/API/1.1/depositos`: cubierto=`[GET]`
- `/API/1.1/identificacionTributaria`: cubierto=`[GET]`
- `/API/1.1/listaPrecioBean`: cubierto=`[GET, POST]`
- `/API/1.1/listaPrecioBean/{id}`: cubierto=`[DELETE, GET, PATCH, PUT]`
- `/API/1.1/monedaBean`: cubierto=`[GET]`
- `/API/1.1/remitoVentaBean`: cubierto=`[GET, POST, PUT]`
- `/API/1.1/remitoVentaBean/{id}`: cubierto=`[DELETE]` | local-extra=`[GET, PATCH, PUT]`
- `/API/1.1/vendedorBean`: cubierto=`[GET]`

## Endpoints locales fuera de Swagger oficial (extensiones formales acordadas)
- `/API/1.1/ProductoCompraBean/{id}` `[GET]`
- `/API/1.1/categoriaFiscal/{id}` `[GET]`
- `/API/1.1/depositos/{id}` `[GET]`
- `/API/1.1/identificacionTributaria/{id}` `[GET]`
- `/API/1.1/monedaBean/{id}` `[GET]`
- `/API/1.1/vendedorBean/{id}` `[GET]`

Observaciones:
- Se incorporo `PUT /API/1.1/remitoVentaBean` alineado a Swagger (update por `transaccionId` en body).
- `PUT /API/1.1/remitoVentaBean/{id}` se mantiene como extension local de compatibilidad.
- Se decide mantener los `GET .../{id}` de catalogos fuera de Swagger como extension formal del contrato local.

## Pendientes (To Do List)

### Alta prioridad (alineacion de contrato)
1. [x] Alinear paths de productos al contrato oficial:
   - `GET/POST /API/1.1/ProductoVentaBean`
   - `PUT/PATCH/DELETE /API/1.1/ProductoVentaBean/{id}`
   - `GET /API/1.1/ProductoCompraBean`
2. [x] Definir y alinear estrategia para update de remito segun Swagger:
   - agregar `PUT /API/1.1/remitoVentaBean` o documentar desviacion como contrato local.
3. [x] Completar operaciones faltantes de Lista de Precio:
   - `POST /API/1.1/listaPrecioBean`
   - `PUT/PATCH/DELETE /API/1.1/listaPrecioBean/{id}`
4. [x] Decidir si mantener endpoints locales no documentados en Swagger (`.../{id}` de catalogos) como extension formal.
   - Se mantienen como contrato local estable para compatibilidad y DX.

### Media prioridad (expansion funcional)
1. Incorporar recursos contables/comerciales ya publicados en Swagger:
   - `comprobanteCompraBean`, `cobranzaBean`, `pagoBean`,
     `ordenCompraBean`, `presupuestoBean`, `cuenta`.
   - `comprobanteVentaBean` queda parcial: falta `POST`, `PUT` y `DELETE`.
2. Incorporar catalogos de soporte:
   - `banco`, `categoriaCuenta`, `centroDeCostoBean`, `circuitoContableBean`,
     `provinciaBean`, `localidadBean`, `tasaImpositiva`, `unidadMedida`, `talonario`.

### Baja prioridad (integraciones accesorias)
1. Evaluar endpoints auxiliares:
   - `imprimirPDF`, `facturar`, `solicitarCAE`, `enviarTransaccionPorMail`,
     `relacionFacturaNotaDeCredito`.
2. Agregar tracking de estado por endpoint en roadmap tecnico (owner, fase, fecha objetivo).

## Pendientes por recurso (resumen de brecha)
- `ProveedorBean`: 5 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:1`)
- `ajusteStockBean`: 5 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:1`)
- `asientoContableManualBean`: 5 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:1`)
- `banco`: 1 ops pendientes (`GET:1`)
- `categoriaCuenta`: 1 ops pendientes (`GET:1`)
- `centroDeCostoBean`: 1 ops pendientes (`GET:1`)
- `circuitoContableBean`: 1 ops pendientes (`GET:1`)
- `cobranzaBean`: 4 ops pendientes (`DELETE:1, GET:1, POST:1, PUT:1`)
- `comprobanteCompraBean`: 5 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:1`)
- `comprobanteVentaBean`: 3 ops pendientes (`DELETE:1, POST:1, PUT:1`)
- `comprobantesAsociados`: 1 ops pendientes (`GET:1`)
- `cuenta`: 3 ops pendientes (`GET:2, POST:1`)
- `enviarTransaccionPorMail`: 1 ops pendientes (`POST:1`)
- `facturar`: 1 ops pendientes (`POST:1`)
- `imprimirPDF`: 1 ops pendientes (`GET:1`)
- `localidadBean`: 1 ops pendientes (`GET:1`)
- `miempresa`: 1 ops pendientes (`GET:1`)
- `ordenCompraBean`: 5 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:1`)
- `pagoBean`: 2 ops pendientes (`GET:1, POST:1`)
- `paisBean`: 1 ops pendientes (`GET:1`)
- `percepcionBean`: 1 ops pendientes (`GET:1`)
- `presupuestoBean`: 6 ops pendientes (`DELETE:1, GET:2, POST:1, PUT:2`)
- `productoStock`: 2 ops pendientes (`GET:2`)
- `provinciaBean`: 1 ops pendientes (`GET:1`)
- `puntoVentaBean`: 1 ops pendientes (`GET:1`)
- `relacionFacturaNotaDeCredito`: 1 ops pendientes (`GET:1`)
- `retencionBean`: 1 ops pendientes (`GET:1`)
- `solicitarCAE`: 1 ops pendientes (`POST:1`)
- `sucursalClienteBean`: 4 ops pendientes (`DELETE:1, GET:1, POST:1, PUT:1`)
- `talonario`: 1 ops pendientes (`GET:1`)
- `talonarioCobranza`: 1 ops pendientes (`GET:1`)
- `tasaImpositiva`: 1 ops pendientes (`GET:1`)
- `transporteBean`: 4 ops pendientes (`DELETE:1, GET:1, POST:1, PUT:1`)
- `unidadMedida`: 1 ops pendientes (`GET:1`)
- `vendedorBean`: 3 ops pendientes (`DELETE:1, POST:1, PUT:1`)
