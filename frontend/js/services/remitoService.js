import { API_ENDPOINTS, FALLBACK_REMITOS } from "../config.js";
import { getJson } from "./httpClient.js";

function normalizeRemitos(payload) {
  if (Array.isArray(payload?.items)) {
    return payload.items;
  }
  if (Array.isArray(payload)) {
    return payload;
  }
  return [];
}

export async function fetchRemitos() {
  const payload = await getJson(API_ENDPOINTS.remitos);
  return normalizeRemitos(payload);
}

export function getFallbackRemitos() {
  return JSON.parse(JSON.stringify(FALLBACK_REMITOS));
}
