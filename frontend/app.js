const TABLE_COLUMNS = [
  "transaccionId",
  "numeroRemito",
  "fecha",
  "observacion",
  "clienteId",
  "comisionVendedor",
  "depositoId",
  "circuitoContableId"
];

const FALLBACK_REMITO = {
  transaccionId: 38925753,
  numeroRemito: "X-0001-00000064",
  fecha: "2023-06-01",
  observacion: "VALOR DECLARADO $340.500  ",
  clienteId: 5182181,
  comisionVendedor: 0,
  depositoId: -2,
  circuitoContableId: -2
};

function clearTable(tableBody) {
  tableBody.innerHTML = "";
}

function appendMessageRow(tableBody, message) {
  const row = document.createElement("tr");
  const cell = document.createElement("td");
  cell.colSpan = TABLE_COLUMNS.length;
  cell.className = "text-center text-secondary py-3";
  cell.textContent = message;
  row.appendChild(cell);
  tableBody.appendChild(row);
}

function appendRemitoRow(tableBody, remito) {
  const row = document.createElement("tr");

  TABLE_COLUMNS.forEach((column) => {
    const cell = document.createElement("td");
    const value = remito[column];
    cell.textContent = value == null ? "" : String(value);
    row.appendChild(cell);
  });

  tableBody.appendChild(row);
}

function renderRemitos(remitos) {
  const tableBody = document.getElementById("remito-table-body");
  clearTable(tableBody);

  if (remitos.length === 0) {
    appendMessageRow(tableBody, "No hay remitos para mostrar.");
    return;
  }

  remitos.forEach((remito) => {
    appendRemitoRow(tableBody, remito);
  });
}

async function loadRemitos() {
  try {
    const response = await fetch("/API/1.1/remitoVentaBean", {
      headers: { Accept: "application/json" }
    });

    if (!response.ok) {
      throw new Error(`Error HTTP ${response.status}`);
    }

    const payload = await response.json();
    const remitos = Array.isArray(payload?.items)
      ? payload.items
      : Array.isArray(payload)
        ? payload
        : [];

    renderRemitos(remitos);
  } catch (error) {
    console.error("No se pudo cargar la lista de remitos:", error);
    renderRemitos([FALLBACK_REMITO]);
  }
}

loadRemitos();
