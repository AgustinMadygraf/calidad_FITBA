const QUERY_KEYS = {
  remitoVenta: "remitoVenta",
  cliente: "cliente",
  producto: "producto"
};

const ROUTE_INDEX_KEY = "__xubioRouteIndex";

function parseRouteIndex(value) {
  const numeric = Number(value);
  if (!Number.isInteger(numeric) || numeric < 0) {
    return 0;
  }
  return numeric;
}

let currentRouteIndex = parseRouteIndex(window.history.state?.[ROUTE_INDEX_KEY]);

function normalizeQueryValue(value) {
  if (value === null || value === undefined) {
    return null;
  }
  const normalized = String(value).trim();
  return normalized ? normalized : null;
}

function buildRouteState(routeIndex) {
  const previousState =
    window.history.state && typeof window.history.state === "object"
      ? window.history.state
      : {};
  return {
    ...previousState,
    [ROUTE_INDEX_KEY]: routeIndex
  };
}

export function ensureRouteHistoryState() {
  const stateIndex = parseRouteIndex(window.history.state?.[ROUTE_INDEX_KEY]);
  if (stateIndex === currentRouteIndex) {
    return;
  }
  currentRouteIndex = stateIndex;
  window.history.replaceState(
    buildRouteState(currentRouteIndex),
    "",
    `${window.location.pathname}${window.location.search}${window.location.hash}`
  );
}

export function syncRouteHistoryOnPopState(state) {
  currentRouteIndex = parseRouteIndex(state?.[ROUTE_INDEX_KEY]);
}

export function hasInAppHistory() {
  return currentRouteIndex > 0;
}

function setOrDeleteParam(params, key, value) {
  const normalized = normalizeQueryValue(value);
  if (normalized === null) {
    params.delete(key);
    return;
  }
  params.set(key, normalized);
}

export function readRouteFromUrl(search = window.location.search) {
  const params = new URLSearchParams(search);
  return {
    remitoVentaId: normalizeQueryValue(params.get(QUERY_KEYS.remitoVenta)),
    clienteId: normalizeQueryValue(params.get(QUERY_KEYS.cliente)),
    productoId: normalizeQueryValue(params.get(QUERY_KEYS.producto))
  };
}

export function writeRouteToUrl({
  remitoVentaId = null,
  clienteId = null,
  productoId = null
}, { mode = "push" } = {}) {
  const params = new URLSearchParams(window.location.search);

  setOrDeleteParam(params, QUERY_KEYS.remitoVenta, remitoVentaId);
  setOrDeleteParam(params, QUERY_KEYS.cliente, clienteId);
  setOrDeleteParam(params, QUERY_KEYS.producto, productoId);

  const query = params.toString();
  const nextUrl = `${window.location.pathname}${query ? `?${query}` : ""}${
    window.location.hash
  }`;
  const currentUrl = `${window.location.pathname}${window.location.search}${window.location.hash}`;
  if (nextUrl === currentUrl) {
    return;
  }

  if (mode === "replace") {
    window.history.replaceState(buildRouteState(currentRouteIndex), "", nextUrl);
    return;
  }

  currentRouteIndex += 1;
  window.history.pushState(buildRouteState(currentRouteIndex), "", nextUrl);
}
