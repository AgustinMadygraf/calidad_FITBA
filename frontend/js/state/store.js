import { MODES, transitionMode } from "./modeMachine.js";

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

function createListaPreciosState() {
  return {
    status: "idle",
    items: [],
    errorMessage: null
  };
}

function createInitialState() {
  return {
    remitos: [],
    mainTable: MODES.NONE,
    selectedTransaccionId: null,
    productoDetail: createProductoDetail(),
    clienteDetail: createClienteDetail(),
    listaPrecios: createListaPreciosState(),
    banner: null
  };
}

let state = createInitialState();
const listeners = new Set();

function normalizeId(value) {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  return String(value);
}

function updateState(updater) {
  state = updater(state);
  if (listeners.size > 0) {
    listeners.forEach((listener) => {
      try {
        listener();
      } catch (error) {
        console.error("Error en listener de estado:", error);
      }
    });
  }
  return state;
}

export function getState() {
  return cloneValue(state);
}

export function subscribe(listener) {
  if (typeof listener !== "function") {
    throw new Error("Listener de estado invalido");
  }

  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function setRemitos(remitos) {
  updateState((current) => ({
    ...current,
    remitos: Array.isArray(remitos) ? cloneValue(remitos) : []
  }));
}

export function setListaPreciosLoading() {
  updateState((current) => ({
    ...current,
    listaPrecios: {
      status: "loading",
      items: [],
      errorMessage: null
    }
  }));
}

export function setListaPreciosReady(items) {
  updateState((current) => ({
    ...current,
    listaPrecios: {
      status: "ready",
      items: Array.isArray(items) ? cloneValue(items) : [],
      errorMessage: null
    }
  }));
}

export function setListaPreciosError(errorMessage) {
  updateState((current) => ({
    ...current,
    listaPrecios: {
      status: "error",
      items: [],
      errorMessage
    }
  }));
}

export function resetListaPrecios() {
  updateState((current) => ({
    ...current,
    listaPrecios: createListaPreciosState()
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
  setMainTable(MODES.CLIENTE);
}

export function showProductoAsMainTable() {
  setMainTable(MODES.PRODUCTO);
}

export function showRemitoAsMainTable() {
  setMainTable(MODES.REMITO);
}

export function showListaPrecioAsMainTable() {
  setMainTable(MODES.LISTA_PRECIO);
}

export function showEmptyMainTable() {
  setMainTable(MODES.NONE);
}

export function setMainTable(nextMode) {
  updateState((current) => ({
    ...current,
    mainTable: transitionMode(current.mainTable, nextMode)
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
