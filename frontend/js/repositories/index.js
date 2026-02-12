import { API_ENDPOINTS, FALLBACK_REMITOS } from "../config.js";
import { normalizeRemitosPayload } from "../domain/mappers/remitoMapper.js";
import { normalizeListaPreciosPayload } from "../domain/mappers/listaPrecioMapper.js";
import { toClienteVM } from "../domain/mappers/clienteMapper.js";
import { toProductoVM } from "../domain/mappers/productoMapper.js";
import { HttpError, getJson } from "../services/httpClient.js";

function resolveRepositoryMode() {
  if (typeof window === "undefined") {
    return "http";
  }

  const params = new URLSearchParams(window.location.search);
  const queryMode = params.get("mock");
  if (queryMode === "1" || queryMode === "true") {
    return "mock";
  }

  if (window.__USE_MOCKS__ === true) {
    return "mock";
  }

  try {
    if (window.localStorage?.getItem("USE_MOCKS") === "true") {
      return "mock";
    }
  } catch (error) {
    console.warn("No se pudo leer USE_MOCKS desde localStorage.", error);
  }

  return "http";
}

function createHttpRepositories() {
  return {
    remito: {
      async list() {
        const payload = await getJson(API_ENDPOINTS.remitos);
        return normalizeRemitosPayload(payload);
      }
    },
    listaPrecio: {
      async list() {
        const payload = await getJson(API_ENDPOINTS.listaPrecios);
        return normalizeListaPreciosPayload(payload);
      }
    },
    cliente: {
      async getById(clienteId) {
        const safeClienteId = encodeURIComponent(String(clienteId));
        const endpoint = `${API_ENDPOINTS.clientes}/${safeClienteId}`;

        try {
          const payload = await getJson(endpoint);
          return toClienteVM(payload);
        } catch (error) {
          if (error instanceof HttpError && error.status === 404) {
            return null;
          }
          throw error;
        }
      }
    },
    producto: {
      async getById(productoId) {
        const safeProductoId = encodeURIComponent(String(productoId));
        const endpoint = `${API_ENDPOINTS.productos}/${safeProductoId}`;

        try {
          const payload = await getJson(endpoint);
          return toProductoVM(payload);
        } catch (error) {
          if (error instanceof HttpError && error.status === 404) {
            return null;
          }
          throw error;
        }
      }
    }
  };
}

function createMockRepositories() {
  return {
    remito: {
      async list() {
        return normalizeRemitosPayload(JSON.parse(JSON.stringify(FALLBACK_REMITOS)));
      }
    },
    listaPrecio: {
      async list() {
        return normalizeListaPreciosPayload([]);
      }
    },
    cliente: {
      async getById() {
        return null;
      }
    },
    producto: {
      async getById() {
        return null;
      }
    }
  };
}

export function createRepositories({ mode } = {}) {
  const resolvedMode = mode ?? resolveRepositoryMode();
  return resolvedMode === "mock" ? createMockRepositories() : createHttpRepositories();
}
