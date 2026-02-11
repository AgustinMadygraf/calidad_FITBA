import { API_ENDPOINTS } from "../config.js";
import { HttpError, getJson } from "./httpClient.js";

export async function fetchClienteById(clienteId) {
  const safeClienteId = encodeURIComponent(String(clienteId));
  const endpoint = `${API_ENDPOINTS.clientes}/${safeClienteId}`;

  try {
    return await getJson(endpoint);
  } catch (error) {
    if (error instanceof HttpError && error.status === 404) {
      return null;
    }
    throw error;
  }
}
