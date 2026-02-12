import { formatFechaDDMMYY } from "../domain/dateUtils.js";

export const REMITO_COLUMNS = [
  { key: "transaccionId", linkType: "transaccion" },
  { key: "numeroRemito", className: "text-nowrap" },
  {
    key: "fecha",
    className: "text-nowrap",
    getValue: (remito) => formatFechaDDMMYY(remito?.fecha)
  },
  { key: "observacion", className: "remito-observacion" },
  {
    key: "clienteId",
    linkType: "cliente",
    getValue: (remito) =>
      remito?.clienteId ?? remito?.cliente_id ?? remito?.relaciones?.clienteId
  },
  {
    key: "comisionVendedor",
    className: "text-nowrap",
    getValue: (remito) =>
      remito?.comisionVendedor ?? remito?.relaciones?.comisionVendedor
  },
  {
    key: "depositoID",
    className: "text-nowrap",
    getValue: (remito) =>
      remito?.depositoID ?? remito?.depositoId ?? remito?.relaciones?.depositoId
  },
  {
    key: "circuitoContableId",
    className: "text-nowrap",
    getValue: (remito) =>
      remito?.circuitoContableId ??
      remito?.circuitoContableID ??
      remito?.relaciones?.circuitoContableId
  }
];

export const ITEM_COLUMNS = [
  { key: "transaccionCVItemId" },
  { key: "transaccionId" },
  {
    key: "productoID",
    linkType: "producto",
    getValue: (item) => item?.producto?.ID
  },
  {
    key: "productoid",
    linkType: "producto",
    getValue: (item) => item?.producto?.id
  },
  { key: "descripcion" },
  { key: "cantidad" },
  { key: "precio" }
];

export const PRODUCTO_COLUMNS = [
  {
    key: "productoid",
    getValue: (producto) =>
      producto?.productoid ??
      producto?.productoID ??
      producto?.id ??
      producto?.ID
  },
  { key: "nombre" },
  { key: "codigo" },
  { key: "usrcode", getValue: (producto) => producto?.usrcode ?? producto?.usrCode },
  { key: "codigoBarra" },
  {
    key: "unidadMedida",
    getValue: (producto) =>
      producto?.unidadMedida?.ID ?? producto?.unidadMedida?.id
  },
  { key: "categoria" },
  { key: "stockNegativo" },
  {
    key: "tasaIva",
    getValue: (producto) => producto?.tasaIva?.ID ?? producto?.tasaIva?.id
  },
  {
    key: "cuentaContable",
    getValue: (producto) =>
      producto?.cuentaContable?.ID ?? producto?.cuentaContable?.id
  },
  { key: "catFormIVA2002" },
  { key: "precioUltCompra" },
  { key: "activo" },
  { key: "sincronizaStock" }
];

export const LISTA_PRECIO_COLUMNS = [
  {
    key: "listaPrecioID",
    getValue: (listaPrecio) =>
      listaPrecio?.listaPrecioID ??
      listaPrecio?.listaPrecioId ??
      listaPrecio?.ID ??
      listaPrecio?.id
  },
  { key: "nombre" },
  {
    key: "descripcion",
    getValue: (listaPrecio) => listaPrecio?.descripcion ?? listaPrecio?.detalle
  },
  { key: "activo" }
];

export const COMPROBANTE_VENTA_COLUMNS = [
  { key: "transaccionid" },
  { key: "nombre" },
  {
    key: "fecha",
    className: "text-nowrap",
    getValue: (comprobante) => formatFechaDDMMYY(comprobante?.fecha)
  },
  { key: "clienteNombre", className: "text-nowrap" },
  { key: "vendedorNombre", className: "text-nowrap" },
  { key: "importetotal", className: "text-nowrap" },
  { key: "externalId", className: "text-nowrap" }
];

export const PRODUCTO_NESTED_ITEM_COLUMNS = [
  { key: "ID" },
  { key: "nombre" },
  { key: "codigo" },
  { key: "id" }
];

export const CLIENTE_COLUMNS = [
  { key: "cliente_id" },
  { key: "nombre", className: "cliente-no-wrap-no-truncate" },
  { key: "razonSocial", className: "cliente-no-wrap-no-truncate" },
  {
    key: "identificacionTributaria",
    getValue: (cliente) =>
      cliente?.identificacionTributaria?.ID ??
      cliente?.identificacionTributaria?.id
  },
  {
    key: "categoriaFiscal",
    getValue: (cliente) =>
      cliente?.categoriaFiscal?.ID ?? cliente?.categoriaFiscal?.id
  },
  { key: "cuit", className: "cliente-no-wrap-no-truncate" },
  { key: "CUIT", className: "cliente-no-wrap-no-truncate" },
  { key: "responsabilidadOrganizacionItem" },
  { key: "esclienteextranjero" },
  { key: "esProveedor" },
  { key: "direccion", className: "cliente-no-wrap-no-truncate" },
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
