function cloneValue(value) {
  if (Array.isArray(value)) {
    return value.map(cloneValue);
  }

  if (value && typeof value === "object") {
    const cloned = {};
    Object.entries(value).forEach(([key, nestedValue]) => {
      cloned[key] = cloneValue(nestedValue);
    });
    return cloned;
  }

  return value;
}

function createProductoDetail() {
  return {
    productoId: null,
    status: "idle",
    data: null,
    errorMessage: null
  };
}

function createClienteDetail() {
  return {
    clienteId: null,
    status: "idle",
    data: null,
    errorMessage: null
  };
}

function createInitialState() {
  return {
    remitos: [],
    mainTable: "remito",
    selectedTransaccionId: null,
    productoDetail: createProductoDetail(),
    clienteDetail: createClienteDetail(),
    banner: null
  };
}

let state = createInitialState();

function normalizeId(value) {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  return String(value);
}

function updateState(updater) {
  state = updater(state);
  return state;
}

export function getState() {
  return cloneValue(state);
}

export function setRemitos(remitos) {
  updateState((current) => ({
    ...current,
    remitos: Array.isArray(remitos) ? cloneValue(remitos) : []
  }));
}

export function setBanner(message, variant = "warning") {
  updateState((current) => ({
    ...current,
    banner: { message, variant }
  }));
}

export function clearBanner() {
  updateState((current) => ({
    ...current,
    banner: null
  }));
}

export function clearSelection() {
  updateState((current) => ({
    ...current,
    mainTable: "remito",
    selectedTransaccionId: null,
    productoDetail: createProductoDetail(),
    clienteDetail: createClienteDetail()
  }));
}

export function selectTransaccion(transaccionId) {
  updateState((current) => ({
    ...current,
    selectedTransaccionId: normalizeId(transaccionId),
    productoDetail: createProductoDetail(),
    clienteDetail: createClienteDetail()
  }));
}

export function setProductoLoading(productoId) {
  updateState((current) => ({
    ...current,
    productoDetail: {
      productoId: normalizeId(productoId),
      status: "loading",
      data: null,
      errorMessage: null
    }
  }));
}

export function setProductoReady(productoId, productoData) {
  updateState((current) => ({
    ...current,
    productoDetail: {
      productoId: normalizeId(productoId),
      status: "ready",
      data: cloneValue(productoData),
      errorMessage: null
    }
  }));
}

export function setProductoNotFound(productoId) {
  updateState((current) => ({
    ...current,
    productoDetail: {
      productoId: normalizeId(productoId),
      status: "not_found",
      data: null,
      errorMessage: null
    }
  }));
}

export function setProductoError(productoId, errorMessage) {
  updateState((current) => ({
    ...current,
    productoDetail: {
      productoId: normalizeId(productoId),
      status: "error",
      data: null,
      errorMessage
    }
  }));
}

export function resetProductoDetail() {
  updateState((current) => ({
    ...current,
    productoDetail: createProductoDetail()
  }));
}

export function setClienteLoading(clienteId) {
  updateState((current) => ({
    ...current,
    clienteDetail: {
      clienteId: normalizeId(clienteId),
      status: "loading",
      data: null,
      errorMessage: null
    }
  }));
}

export function setClienteReady(clienteId, clienteData) {
  updateState((current) => ({
    ...current,
    clienteDetail: {
      clienteId: normalizeId(clienteId),
      status: "ready",
      data: cloneValue(clienteData),
      errorMessage: null
    }
  }));
}

export function setClienteNotFound(clienteId) {
  updateState((current) => ({
    ...current,
    clienteDetail: {
      clienteId: normalizeId(clienteId),
      status: "not_found",
      data: null,
      errorMessage: null
    }
  }));
}

export function setClienteError(clienteId, errorMessage) {
  updateState((current) => ({
    ...current,
    clienteDetail: {
      clienteId: normalizeId(clienteId),
      status: "error",
      data: null,
      errorMessage
    }
  }));
}

export function resetClienteDetail() {
  updateState((current) => ({
    ...current,
    clienteDetail: createClienteDetail()
  }));
}

export function showClienteAsMainTable() {
  updateState((current) => ({
    ...current,
    mainTable: "cliente"
  }));
}

export function showProductoAsMainTable() {
  updateState((current) => ({
    ...current,
    mainTable: "producto"
  }));
}

export function showRemitoAsMainTable() {
  updateState((current) => ({
    ...current,
    mainTable: "remito"
  }));
}

export function getVisibleRemitos() {
  const visible =
    state.selectedTransaccionId === null
      ? state.remitos
      : state.remitos.filter(
          (remito) => String(remito?.transaccionId) === state.selectedTransaccionId
        );
  return cloneValue(visible);
}

export function getSelectedRemito() {
  if (state.selectedTransaccionId === null) {
    return null;
  }

  const found =
    state.remitos.find(
      (remito) => String(remito?.transaccionId) === state.selectedTransaccionId
    ) ?? null;

  return cloneValue(found);
}
