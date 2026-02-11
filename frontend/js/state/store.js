const state = {
  remitos: [],
  selectedTransaccionId: null,
  clienteDetail: {
    clienteId: null,
    status: "idle",
    data: null,
    errorMessage: null
  },
  banner: null
};

function normalizeId(value) {
  if (value === undefined || value === null || value === "") {
    return null;
  }
  return String(value);
}

export function getState() {
  return state;
}

export function setRemitos(remitos) {
  state.remitos = Array.isArray(remitos) ? remitos : [];
}

export function setBanner(message, variant = "warning") {
  state.banner = { message, variant };
}

export function clearBanner() {
  state.banner = null;
}

export function clearSelection() {
  state.selectedTransaccionId = null;
  resetClienteDetail();
}

export function selectTransaccion(transaccionId) {
  state.selectedTransaccionId = normalizeId(transaccionId);
  resetClienteDetail();
}

export function setClienteLoading(clienteId) {
  state.clienteDetail = {
    clienteId: normalizeId(clienteId),
    status: "loading",
    data: null,
    errorMessage: null
  };
}

export function setClienteReady(clienteId, clienteData) {
  state.clienteDetail = {
    clienteId: normalizeId(clienteId),
    status: "ready",
    data: clienteData,
    errorMessage: null
  };
}

export function setClienteNotFound(clienteId) {
  state.clienteDetail = {
    clienteId: normalizeId(clienteId),
    status: "not_found",
    data: null,
    errorMessage: null
  };
}

export function setClienteError(clienteId, errorMessage) {
  state.clienteDetail = {
    clienteId: normalizeId(clienteId),
    status: "error",
    data: null,
    errorMessage
  };
}

export function resetClienteDetail() {
  state.clienteDetail = {
    clienteId: null,
    status: "idle",
    data: null,
    errorMessage: null
  };
}

export function getVisibleRemitos() {
  if (state.selectedTransaccionId === null) {
    return state.remitos;
  }

  return state.remitos.filter(
    (remito) => String(remito?.transaccionId) === state.selectedTransaccionId
  );
}

export function getSelectedRemito() {
  if (state.selectedTransaccionId === null) {
    return null;
  }

  return (
    state.remitos.find(
      (remito) => String(remito?.transaccionId) === state.selectedTransaccionId
    ) ?? null
  );
}
