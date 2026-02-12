import { API_ENDPOINTS } from "../config.js";
import { normalizeListaPreciosPayload } from "../domain/mappers/listaPrecioMapper.js";
import { getJson } from "./httpClient.js";

export async function fetchListaPrecios() {
  const payload = await getJson(API_ENDPOINTS.listaPrecios);
  return normalizeListaPreciosPayload(payload);
}
