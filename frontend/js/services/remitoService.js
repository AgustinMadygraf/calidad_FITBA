import { API_ENDPOINTS, FALLBACK_REMITOS } from "../config.js";
import { normalizeRemitosPayload } from "../domain/mappers/remitoMapper.js";
import { getJson } from "./httpClient.js";

export async function fetchRemitos() {
  const payload = await getJson(API_ENDPOINTS.remitos);
  return normalizeRemitosPayload(payload);
}

export function getFallbackRemitos() {
  return normalizeRemitosPayload(JSON.parse(JSON.stringify(FALLBACK_REMITOS)));
}
