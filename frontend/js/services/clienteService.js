import { API_ENDPOINTS } from "../config.js";
import { toClienteVM } from "../domain/mappers/clienteMapper.js";
import { HttpError, getJson } from "./httpClient.js";

export async function fetchClienteById(clienteId) {
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
