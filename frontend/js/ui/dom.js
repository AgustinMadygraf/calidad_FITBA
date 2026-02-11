function getById(id) {
  const node = document.getElementById(id);
  if (!node) {
    throw new Error(`No se encontro el nodo requerido con id "${id}"`);
  }
  return node;
}

export function getDomRefs() {
  return {
    banner: getById("status-banner"),
    mainTitle: getById("main-title"),
    showAllButton: getById("show-all-btn"),
    remitoTableWrapper: getById("remito-table-wrapper"),
    remitoTableBody: getById("remito-table-body"),
    clienteMainTableWrapper: getById("cliente-main-table-wrapper"),
    clienteMainTableBody: getById("cliente-main-table-body"),
    productoMainTableWrapper: getById("producto-main-table-wrapper"),
    productoMainTableBody: getById("producto-main-table-body"),
    productoUnidadMedidaSection: getById("producto-unidad-medida-section"),
    productoUnidadMedidaTitle: getById("producto-unidad-medida-title"),
    productoUnidadMedidaTableBody: getById("producto-unidad-medida-table-body"),
    productoTasaIvaSection: getById("producto-tasa-iva-section"),
    productoTasaIvaTitle: getById("producto-tasa-iva-title"),
    productoTasaIvaTableBody: getById("producto-tasa-iva-table-body"),
    productoCuentaContableSection: getById("producto-cuenta-contable-section"),
    productoCuentaContableTitle: getById("producto-cuenta-contable-title"),
    productoCuentaContableTableBody: getById("producto-cuenta-contable-table-body"),
    itemSection: getById("detalle-section"),
    itemTitle: getById("detalle-title"),
    itemTableBody: getById("items-table-body"),
    clienteSection: getById("cliente-section"),
    clienteTitle: getById("cliente-title"),
    clienteTableBody: getById("cliente-table-body"),
    identificacionTributariaSection: getById("identificacion-tributaria-section"),
    identificacionTributariaTitle: getById("identificacion-tributaria-title"),
    identificacionTributariaTableBody: getById(
      "identificacion-tributaria-table-body"
    ),
    categoriaFiscalSection: getById("categoria-fiscal-section"),
    categoriaFiscalTitle: getById("categoria-fiscal-title"),
    categoriaFiscalTableBody: getById("categoria-fiscal-table-body")
  };
}
