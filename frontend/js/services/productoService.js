import { API_ENDPOINTS } from "../config.js";
import { toProductoVM } from "../domain/mappers/productoMapper.js";
import { HttpError, getJson } from "./httpClient.js";

export async function fetchProductoById(productoId) {
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
