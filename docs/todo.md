# TODO Tecnico

Documento de trabajo para ejecutar mejoras de arquitectura, testing y frontend.

## Decisiones vigentes

- Compatibilidad total con Xubio: no romper contrato de endpoints ni nombres de campos.
- Migracion incremental a Vue: sin reescritura total.
- Runtime objetivo actual: single-instance.

## Fase 0 - Estabilizacion de testing HTTP (bloqueante)

- [ ] T0.1 Definir matriz de versiones compatibles para pruebas HTTP.
  Descripcion: registrar combinacion estable de `fastapi`, `starlette`, `httpx`, `anyio`, `pytest`, `pytest-cov`.
  Entregable: tabla en este documento + actualizacion de `requirements.txt`.
  Criterio de aceptacion: una app FastAPI minima responde en prueba automatica sin cuelgues.
  Complejidad: Media.
  Dependencias: ninguna.

- [ ] T0.2 Agregar smoke test minimo de transporte HTTP.
  Descripcion: crear test aislado que valide `GET /health` con cliente de pruebas.
  Entregable: archivo de test dedicado para detectar incompatibilidad de stack.
  Criterio de aceptacion: el test falla rapido con mensaje claro si hay cuelgue/incompatibilidad.
  Complejidad: Baja.
  Dependencias: T0.1.

- [ ] T0.3 Separar suites de test por tipo.
  Descripcion: etiquetar tests en `unit`, `integration`, `api_http`, `contract` para ejecutar pipelines parciales.
  Entregable: markers en pytest + comando documentado por suite.
  Criterio de aceptacion: se pueden correr suites independientes sin depender de toda la bateria.
  Complejidad: Baja.
  Dependencias: T0.1.

## Fase 1 - Modularizacion backend (Clean Architecture aplicada)

- [ ] T1.1 Extraer routers por recurso desde `src/infrastructure/fastapi/api.py`.
  Descripcion: mover rutas de cliente, remito, producto, lista de precio, vendedor, comprobante y catalogos a modulos separados.
  Entregable: paquete `src/infrastructure/fastapi/routers/` con un router por contexto.
  Criterio de aceptacion: `api.py` queda como composition root y registro de routers.
  Complejidad: Alta.
  Dependencias: T0.1.

- [ ] T1.2 Centralizar manejo de errores HTTP.
  Descripcion: reemplazar bloques repetidos `try/except ExternalServiceError` por exception handlers globales.
  Entregable: manejadores globales para `ExternalServiceError` y `ValueError` donde corresponda.
  Criterio de aceptacion: misma semantica HTTP actual (400/404/502/403) con menos duplicacion.
  Complejidad: Media.
  Dependencias: T1.1.

- [ ] T1.3 Consolidar resolucion de gateways en un provider unico.
  Descripcion: eliminar getters repetidos con atributos dinamicos en `app` y usar provider/factory explicita.
  Entregable: modulo de providers desacoplado de rutas.
  Criterio de aceptacion: instanciacion lazy conservada sin duplicacion de codigo.
  Complejidad: Media.
  Dependencias: T1.1.

- [ ] T1.4 Mantener politicas de runtime en middleware dedicado.
  Descripcion: preservar bloqueo de mutaciones en no-prod y reglas de debug, desacoplado del wiring de endpoints.
  Entregable: middleware/policy module con pruebas unitarias.
  Criterio de aceptacion: comportamiento actual sin regresiones funcionales.
  Complejidad: Baja.
  Dependencias: T1.1.

## Fase 2 - Compatibilidad total Xubio con contratos verificables

- [ ] T2.1 Definir matriz de contrato local vs Swagger oficial.
  Descripcion: documentar por endpoint/metodo si es oficial o extension local formal.
  Entregable: actualizacion de `docs/relevamiento_endpoints_xubio.md`.
  Criterio de aceptacion: 100% de rutas locales clasificadas.
  Complejidad: Baja.
  Dependencias: ninguna.

- [ ] T2.2 Implementar contract tests automáticos contra `docs/swagger.json`.
  Descripcion: validar que endpoints oficiales implementados respetan verbos esperados y codigos base.
  Entregable: suite `contract` ejecutable en CI local.
  Criterio de aceptacion: cada cambio de rutas se valida contra contrato.
  Complejidad: Media.
  Dependencias: T0.3.

- [ ] T2.3 Consolidar mapeo de ids/campos variantes en anti-corruption layer.
  Descripcion: centralizar logica `ID/id/...` para evitar divergencia en gateways y mappers.
  Entregable: utilitarios comunes de normalizacion y matching.
  Criterio de aceptacion: no hay logica duplicada de matching de IDs por recurso.
  Complejidad: Media.
  Dependencias: T1.1.

- [ ] T2.4 Endurecer validaciones de payload sin romper compatibilidad externa.
  Descripcion: introducir validaciones internas tipadas manteniendo input/output original de Xubio.
  Entregable: validadores internos y tests de no-regresion de payload.
  Criterio de aceptacion: mismas respuestas externas, menos errores silenciosos internos.
  Complejidad: Alta.
  Dependencias: T2.3.

## Fase 3 - Refactor de gateways y cache (single-instance hoy, escalable manana)

- [ ] T3.1 Crear base comun para gateways HTTPX CRUD.
  Descripcion: extraer comportamiento repetido de list/get/create/update/delete con cache y fallback.
  Entregable: clase/base helper reutilizable por recurso.
  Criterio de aceptacion: menor LOC total y semantica intacta.
  Complejidad: Alta.
  Dependencias: T1.1.

- [ ] T3.2 Encapsular cache en interfaz.
  Descripcion: mantener in-memory por defecto pero ocultar detalles de store global.
  Entregable: contrato `CacheProvider` + implementacion in-memory.
  Criterio de aceptacion: gateways dependen de la interfaz, no de diccionarios globales.
  Complejidad: Media.
  Dependencias: T3.1.

- [ ] T3.3 Preparar adaptador opcional Redis (sin activar por defecto).
  Descripcion: dejar extension preparada para escenario multi-instancia futuro.
  Entregable: implementacion opcional y documentada.
  Criterio de aceptacion: feature flag para seleccionar provider, default in-memory.
  Complejidad: Media.
  Dependencias: T3.2.

## Fase 4 - Frontend incremental a Vue (islands)

- [ ] T4.1 Definir arquitectura de convivencia JS modular + Vue.
  Descripcion: acordar donde montar islas Vue y que parte de estado/control mantiene JS actual.
  Entregable: decision record en docs + guia de integracion.
  Criterio de aceptacion: flujo de trabajo claro para migrar modulo por modulo.
  Complejidad: Baja.
  Dependencias: ninguna.

- [ ] T4.2 Extraer capa de datos compartida para reutilizar en Vue.
  Descripcion: aislar repositorios/client HTTP y mappers para que los use tanto JS actual como Vue.
  Entregable: modulo de data-access estable y testeado.
  Criterio de aceptacion: sin duplicar llamadas API entre implementaciones.
  Complejidad: Media.
  Dependencias: T4.1.

- [ ] T4.3 Migrar modulo "comprobante de venta" a primer island Vue.
  Descripcion: reemplazar render/eventos de ese modulo por componente Vue manteniendo rutas y contrato.
  Entregable: pantalla de listado + detalle en Vue.
  Criterio de aceptacion: mismas funcionalidades actuales (click detalle, volver al listado, estados loading/error/not_found).
  Complejidad: Alta.
  Dependencias: T4.2.

- [ ] T4.4 Reducir tamaño de `appController.js`.
  Descripcion: luego del island, delegar navegacion/orquestacion por modulo y quitar responsabilidades del controlador global.
  Entregable: controlador dividido por dominio funcional.
  Criterio de aceptacion: `appController.js` deja de ser punto unico de cambio.
  Complejidad: Media.
  Dependencias: T4.3.

## Fase 5 - Cobertura y calidad continua

- [ ] T5.1 Incorporar cobertura minima por suite.
  Descripcion: definir umbral por tipo de test (unit/integration/contract/api_http).
  Entregable: configuracion de `pytest-cov` por suite.
  Criterio de aceptacion: falla automatica cuando cobertura cae bajo umbral acordado.
  Complejidad: Baja.
  Dependencias: T0.3.

- [ ] T5.2 Agregar tests frontend.
  Descripcion: pruebas unitarias de mappers/store y e2e de flujos criticos de UI.
  Entregable: setup de test frontend + casos minimos.
  Criterio de aceptacion: flujo principal remito/lista precio/comprobante cubierto.
  Complejidad: Alta.
  Dependencias: T4.2.

- [ ] T5.3 Checklist de release tecnico.
  Descripcion: validar contrato, tests, logs y politicas de runtime antes de merge.
  Entregable: checklist en docs y script de verificacion local.
  Criterio de aceptacion: proceso repetible previo a cada entrega.
  Complejidad: Baja.
  Dependencias: T2.2, T5.1.

## Orden recomendado de ejecucion

1. T0.1 -> T0.2 -> T0.3
2. T1.1 -> T1.2 -> T1.3 -> T1.4
3. T2.1 -> T2.2 -> T2.3 -> T2.4
4. T3.1 -> T3.2 -> T3.3
5. T4.1 -> T4.2 -> T4.3 -> T4.4
6. T5.1 -> T5.2 -> T5.3

