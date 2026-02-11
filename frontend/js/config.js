export const API_ENDPOINTS = {
  remitos: "/API/1.1/remitoVentaBean",
  clientes: "/API/1.1/clienteBean"
};

export const REMITO_COLUMNS = [
  { key: "transaccionId", linkType: "transaccion" },
  { key: "numeroRemito", className: "text-nowrap" },
  { key: "fecha", className: "text-nowrap" },
  { key: "observacion", className: "remito-observacion" },
  { key: "clienteId", linkType: "cliente" },
  { key: "comisionVendedor" },
  { key: "depositoId" },
  { key: "circuitoContableId" }
];

export const ITEM_COLUMNS = [
  { key: "transaccionCVItemId" },
  { key: "transaccionId" },
  { key: "productoID", getValue: (item) => item?.producto?.ID },
  { key: "productoid", getValue: (item) => item?.producto?.id },
  { key: "descripcion" },
  { key: "cantidad" },
  { key: "precio" }
];

export const CLIENTE_COLUMNS = [
  { key: "cliente_id" },
  { key: "nombre" },
  { key: "razonSocial" },
  {
    key: "identificacionTributaria",
    getValue: (cliente) =>
      cliente?.identificacionTributaria?.ID ??
      cliente?.identificacionTributaria?.id
  },
  {
    key: "categoriaFiscal",
    getValue: (cliente) => cliente?.categoriaFiscal?.ID ?? cliente?.categoriaFiscal?.id
  },
  { key: "cuit" },
  { key: "CUIT" },
  { key: "responsabilidadOrganizacionItem" },
  { key: "esclienteextranjero" },
  { key: "esProveedor" },
  { key: "direccion" },
  { key: "email" },
  { key: "telefono" },
  { key: "provincia" },
  { key: "pais" },
  { key: "cuentaVenta_id" },
  { key: "cuentaCompra_id" },
  { key: "usrCode" },
  { key: "descripcion" }
];

export const IDENTIFICACION_TRIBUTARIA_COLUMNS = [
  { key: "ID" },
  { key: "nombre" },
  { key: "codigo" },
  { key: "id" }
];

export const CATEGORIA_FISCAL_COLUMNS = [
  { key: "ID" },
  { key: "nombre" },
  { key: "codigo" },
  { key: "id" }
];

export const FALLBACK_REMITOS = [
  {
    transaccionId: 38925753,
    numeroRemito: "X-0001-00000064",
    fecha: "2023-06-01",
    observacion: "VALOR DECLARADO $340.500  ",
    clienteId: 5182181,
    comisionVendedor: 0,
    depositoId: -2,
    circuitoContableId: -2,
    transaccionProductoItem: [
      {
        transaccionCVItemId: 48344936,
        transaccionId: 38925753,
        producto: {
          ID: 1672624,
          id: 1672624
        },
        descripcion: "12.5x8x19 Bolsa Marron 100g C/M",
        cantidad: 4000,
        precio: 0
      }
    ]
  }
];

export const UI_MESSAGES = {
  remitosLoadError:
    "No se pudo cargar la lista de remitos desde la API. Se muestran datos de ejemplo.",
  noRemitos: "No hay remitos para mostrar.",
  noItems: "Esta transaccion no tiene items.",
  clienteLoading: "Cargando cliente...",
  clienteNotFound: "No se encontro el cliente para el id seleccionado.",
  clienteLoadError: "No se pudo cargar el cliente seleccionado.",
  identificacionTributariaNotFound:
    "El cliente no tiene datos de identificacionTributaria.",
  categoriaFiscalNotFound: "El cliente no tiene datos de categoriaFiscal."
};
