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
    const value = resolveValue(data, column);

    if (column.linkType === "transaccion" && value !== undefined && value !== null) {
      const link = document.createElement("a");
      link.href = "#";
      link.className = "js-transaccion-link";
      link.dataset.transaccionId = asText(value);
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
