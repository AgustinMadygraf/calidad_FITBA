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
    showAllButton: getById("show-all-btn"),
    remitoTableBody: getById("remito-table-body"),
    itemSection: getById("detalle-section"),
    itemTitle: getById("detalle-title"),
    itemTableBody: getById("items-table-body"),
    clienteSection: getById("cliente-section"),
    clienteTitle: getById("cliente-title"),
    clienteTableBody: getById("cliente-table-body")
  };
}
