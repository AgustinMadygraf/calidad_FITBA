function asText(value) {
  if (value === undefined || value === null) {
    return "";
  }
  if (typeof value === "object") {
    return JSON.stringify(value);
  }
  return String(value);
}

function resolveValue(data, column) {
  if (typeof column.getValue === "function") {
    return column.getValue(data);
  }
  return data?.[column.key];
}

function clearTable(tableBody) {
  tableBody.innerHTML = "";
}

function appendMessageRow(tableBody, message, colSpan) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = colSpan;
  cell.className = "text-center text-secondary py-3";
  cell.textContent = message;
  row.appendChild(cell);
  tableBody.appendChild(row);
}

function appendDataRow(tableBody, data, columns) {
  const row = document.createElement("tr");

  columns.forEach((column) => {
    const cell = document.createElement("td");
    if (column.className) {
      cell.classList.add(...String(column.className).split(/\s+/).filter(Boolean));
    }
    const value = resolveValue(data, column);

    if (column.linkType === "transaccion" && value !== undefined && value !== null) {
      const link = document.createElement("a");
      link.href = "#";
      link.className = "js-transaccion-link";
      link.dataset.transaccionId = asText(value);
      link.dataset.clienteId = asText(data?.clienteId ?? data?.cliente_id);
      link.textContent = asText(value);
      cell.appendChild(link);
    } else if (
      column.linkType === "cliente" &&
      value !== undefined &&
      value !== null
    ) {
      const link = document.createElement("a");
      link.href = "#";
      link.className = "js-cliente-link";
      link.dataset.clienteId = asText(value);
      link.dataset.transaccionId = asText(data?.transaccionId);
      link.textContent = asText(value);
      cell.appendChild(link);
    } else if (
      column.linkType === "comprobanteVenta" &&
      value !== undefined &&
      value !== null
    ) {
      const link = document.createElement("a");
      link.href = "#";
      link.className = "js-comprobante-venta-link";
      link.dataset.comprobanteVentaId = asText(value);
      link.textContent = asText(value);
      cell.appendChild(link);
    } else if (
      column.linkType === "producto" &&
      value !== undefined &&
      value !== null
    ) {
      const link = document.createElement("a");
      link.href = "#";
      link.className = "js-producto-link";
      link.dataset.productoId = asText(value);
      link.textContent = asText(value);
      cell.appendChild(link);
    } else {
      cell.textContent = asText(value);
    }

    row.appendChild(cell);
  });

  tableBody.appendChild(row);
}

export function renderBanner(bannerNode, banner) {
  if (!banner) {
    bannerNode.className = "alert alert-warning d-none";
    bannerNode.textContent = "";
    return;
  }

  bannerNode.className = `alert alert-${banner.variant} mb-4`;
  bannerNode.textContent = banner.message;
}

export function renderShowAllButton(showAllButton, hasSelection) {
  showAllButton.classList.toggle("d-none", !hasSelection);
}

export function renderRemitoTable(tableBody, remitos, columns, emptyMessage) {
  clearTable(tableBody);

  if (!Array.isArray(remitos) || remitos.length === 0) {
    appendMessageRow(tableBody, emptyMessage, columns.length);
    return;
  }

  remitos.forEach((remito) => {
    appendDataRow(tableBody, remito, columns);
  });
}

export function renderListaPrecioTable(
  tableBody,
  listaPreciosState,
  columns,
  uiMessages
) {
  clearTable(tableBody);

  if (listaPreciosState?.status === "loading") {
    appendMessageRow(tableBody, uiMessages.listaPrecioLoading, columns.length);
    return;
  }

  if (listaPreciosState?.status === "error") {
    const message =
      listaPreciosState.errorMessage || uiMessages.listaPreciosLoadError;
    appendMessageRow(tableBody, message, columns.length);
    return;
  }

  const items = Array.isArray(listaPreciosState?.items)
    ? listaPreciosState.items
    : [];

  if (items.length === 0) {
    appendMessageRow(tableBody, uiMessages.noListaPrecios, columns.length);
    return;
  }

  items.forEach((item) => {
    appendDataRow(tableBody, item, columns);
  });
}

export function renderComprobanteVentaTable(
  tableBody,
  comprobantesVentaState,
  columns,
  uiMessages
) {
  clearTable(tableBody);

  if (comprobantesVentaState?.status === "loading") {
    appendMessageRow(tableBody, uiMessages.comprobanteVentaLoading, columns.length);
    return;
  }

  if (comprobantesVentaState?.status === "error") {
    const message =
      comprobantesVentaState.errorMessage || uiMessages.comprobantesVentaLoadError;
    appendMessageRow(tableBody, message, columns.length);
    return;
  }

  const items = Array.isArray(comprobantesVentaState?.items)
    ? comprobantesVentaState.items
    : [];

  if (items.length === 0) {
    appendMessageRow(tableBody, uiMessages.noComprobantesVenta, columns.length);
    return;
  }

  items.forEach((item) => {
    appendDataRow(tableBody, item, columns);
  });
}

export function renderComprobanteVentaDetailSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  comprobanteVentaDetail,
  columns,
  uiMessages
) {
  clearTable(tableBodyNode);

  if (comprobanteVentaDetail?.status === "idle") {
    sectionNode.classList.add("d-none");
    return;
  }

  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de comprobante ${asText(
    comprobanteVentaDetail?.comprobanteVentaId
  )}`;

  if (comprobanteVentaDetail?.status === "loading") {
    appendMessageRow(
      tableBodyNode,
      uiMessages.comprobanteVentaDetailLoading,
      columns.length
    );
    return;
  }

  if (comprobanteVentaDetail?.status === "not_found") {
    appendMessageRow(
      tableBodyNode,
      uiMessages.comprobanteVentaDetailNotFound,
      columns.length
    );
    return;
  }

  if (comprobanteVentaDetail?.status === "error") {
    const message =
      comprobanteVentaDetail.errorMessage ||
      uiMessages.comprobanteVentaDetailLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (comprobanteVentaDetail?.status === "ready" && comprobanteVentaDetail.data) {
    appendDataRow(tableBodyNode, comprobanteVentaDetail.data, columns);
    return;
  }

  appendMessageRow(
    tableBodyNode,
    uiMessages.comprobanteVentaDetailLoadError,
    columns.length
  );
}

export function hideDetailSection(sectionNode, tableBodyNode) {
  clearTable(tableBodyNode);
  sectionNode.classList.add("d-none");
}

export function renderItemSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  remito,
  columns,
  emptyMessage
) {
  const items = Array.isArray(remito?.transaccionProductoItem)
    ? remito.transaccionProductoItem
    : [];

  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de items para transaccionId ${asText(
    remito?.transaccionId
  )}`;

  if (items.length === 0) {
    appendMessageRow(tableBodyNode, emptyMessage, columns.length);
    return;
  }

  items.forEach((item) => {
    appendDataRow(tableBodyNode, item, columns);
  });
}

export function renderClienteSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  clienteDetail,
  columns,
  uiMessages
) {
  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de cliente ${asText(clienteDetail?.clienteId)}`;

  if (clienteDetail?.status === "loading") {
    appendMessageRow(tableBodyNode, uiMessages.clienteLoading, columns.length);
    return;
  }

  if (clienteDetail?.status === "not_found") {
    appendMessageRow(tableBodyNode, uiMessages.clienteNotFound, columns.length);
    return;
  }

  if (clienteDetail?.status === "error") {
    const message = clienteDetail.errorMessage || uiMessages.clienteLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (clienteDetail?.status === "ready" && clienteDetail.data) {
    appendDataRow(tableBodyNode, clienteDetail.data, columns);
    return;
  }

  appendMessageRow(tableBodyNode, uiMessages.clienteLoadError, columns.length);
}

export function renderIdentificacionTributariaSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  clienteDetail,
  columns,
  uiMessages
) {
  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de identificacionTributaria para cliente ${asText(
    clienteDetail?.clienteId
  )}`;

  if (clienteDetail?.status === "loading") {
    appendMessageRow(tableBodyNode, uiMessages.clienteLoading, columns.length);
    return;
  }

  if (clienteDetail?.status === "not_found") {
    appendMessageRow(tableBodyNode, uiMessages.clienteNotFound, columns.length);
    return;
  }

  if (clienteDetail?.status === "error") {
    const message = clienteDetail.errorMessage || uiMessages.clienteLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (clienteDetail?.status === "ready" && clienteDetail.data) {
    const identificacionTributaria = clienteDetail.data.identificacionTributaria;
    if (
      identificacionTributaria &&
      typeof identificacionTributaria === "object" &&
      !Array.isArray(identificacionTributaria)
    ) {
      appendDataRow(tableBodyNode, identificacionTributaria, columns);
      return;
    }
    appendMessageRow(
      tableBodyNode,
      uiMessages.identificacionTributariaNotFound,
      columns.length
    );
    return;
  }

  appendMessageRow(tableBodyNode, uiMessages.clienteLoadError, columns.length);
}

export function renderCategoriaFiscalSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  clienteDetail,
  columns,
  uiMessages
) {
  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de categoriaFiscal para cliente ${asText(
    clienteDetail?.clienteId
  )}`;

  if (clienteDetail?.status === "loading") {
    appendMessageRow(tableBodyNode, uiMessages.clienteLoading, columns.length);
    return;
  }

  if (clienteDetail?.status === "not_found") {
    appendMessageRow(tableBodyNode, uiMessages.clienteNotFound, columns.length);
    return;
  }

  if (clienteDetail?.status === "error") {
    const message = clienteDetail.errorMessage || uiMessages.clienteLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (clienteDetail?.status === "ready" && clienteDetail.data) {
    const categoriaFiscal = clienteDetail.data.categoriaFiscal;
    if (
      categoriaFiscal &&
      typeof categoriaFiscal === "object" &&
      !Array.isArray(categoriaFiscal)
    ) {
      appendDataRow(tableBodyNode, categoriaFiscal, columns);
      return;
    }
    appendMessageRow(tableBodyNode, uiMessages.categoriaFiscalNotFound, columns.length);
    return;
  }

  appendMessageRow(tableBodyNode, uiMessages.clienteLoadError, columns.length);
}

export function renderProductoSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  productoDetail,
  columns,
  uiMessages
) {
  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de producto ${asText(productoDetail?.productoId)}`;

  if (productoDetail?.status === "loading") {
    appendMessageRow(tableBodyNode, uiMessages.productoLoading, columns.length);
    return;
  }

  if (productoDetail?.status === "not_found") {
    appendMessageRow(tableBodyNode, uiMessages.productoNotFound, columns.length);
    return;
  }

  if (productoDetail?.status === "error") {
    const message = productoDetail.errorMessage || uiMessages.productoLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (productoDetail?.status === "ready" && productoDetail.data) {
    appendDataRow(tableBodyNode, productoDetail.data, columns);
    return;
  }

  appendMessageRow(tableBodyNode, uiMessages.productoLoadError, columns.length);
}

export function renderProductoNestedSection(
  sectionNode,
  titleNode,
  tableBodyNode,
  productoDetail,
  columns,
  uiMessages,
  { fieldKey, label, notFoundMessageKey }
) {
  clearTable(tableBodyNode);
  sectionNode.classList.remove("d-none");
  titleNode.textContent = `Detalle de ${label} para producto ${asText(
    productoDetail?.productoId
  )}`;

  if (productoDetail?.status === "loading") {
    appendMessageRow(tableBodyNode, uiMessages.productoLoading, columns.length);
    return;
  }

  if (productoDetail?.status === "not_found") {
    appendMessageRow(tableBodyNode, uiMessages.productoNotFound, columns.length);
    return;
  }

  if (productoDetail?.status === "error") {
    const message = productoDetail.errorMessage || uiMessages.productoLoadError;
    appendMessageRow(tableBodyNode, message, columns.length);
    return;
  }

  if (productoDetail?.status === "ready" && productoDetail.data) {
    const nestedValue = productoDetail.data[fieldKey];
    if (
      nestedValue &&
      typeof nestedValue === "object" &&
      !Array.isArray(nestedValue)
    ) {
      appendDataRow(tableBodyNode, nestedValue, columns);
      return;
    }
    appendMessageRow(
      tableBodyNode,
      uiMessages[notFoundMessageKey] || uiMessages.productoLoadError,
      columns.length
    );
    return;
  }

  appendMessageRow(tableBodyNode, uiMessages.productoLoadError, columns.length);
}
