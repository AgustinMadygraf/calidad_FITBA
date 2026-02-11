import { API_ENDPOINTS, FALLBACK_REMITOS } from "../config.js";
import { getJson } from "./httpClient.js";

function parseFechaToTimestamp(fecha) {
  if (fecha === undefined || fecha === null || fecha === "") {
    return Number.NEGATIVE_INFINITY;
  }

  if (typeof fecha === "number") {
    return Number.isFinite(fecha) ? fecha : Number.NEGATIVE_INFINITY;
  }

  const rawValue = String(fecha).trim();
  if (!rawValue) {
    return Number.NEGATIVE_INFINITY;
  }

  const normalizedValue = rawValue.replace(/\s+/g, " ");
  const parsedWithNativeDate = Date.parse(normalizedValue);
  if (Number.isFinite(parsedWithNativeDate)) {
    return parsedWithNativeDate;
  }

  const match = normalizedValue.match(
    /^(\d{1,2})\/(\d{1,2})\/(\d{4})(?:[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?$/
  );
  if (!match) {
    return Number.NEGATIVE_INFINITY;
  }

  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const hour = Number(match[4] ?? 0);
  const minute = Number(match[5] ?? 0);
  const second = Number(match[6] ?? 0);

  return Date.UTC(year, month - 1, day, hour, minute, second);
}

function sortRemitosByFechaDesc(remitos) {
  return [...remitos].sort((left, right) => {
    const timestampDifference =
      parseFechaToTimestamp(right?.fecha) - parseFechaToTimestamp(left?.fecha);
    if (timestampDifference !== 0) {
      return timestampDifference;
    }

    const leftId = Number(left?.transaccionId);
    const rightId = Number(right?.transaccionId);
    if (Number.isFinite(leftId) && Number.isFinite(rightId) && leftId !== rightId) {
      return rightId - leftId;
    }

    return 0;
  });
}

function normalizeRemitos(payload) {
  if (Array.isArray(payload?.items)) {
    return sortRemitosByFechaDesc(payload.items);
  }
  if (Array.isArray(payload)) {
    return sortRemitosByFechaDesc(payload);
  }
  return [];
}

export async function fetchRemitos() {
  const payload = await getJson(API_ENDPOINTS.remitos);
  return normalizeRemitos(payload);
}

export function getFallbackRemitos() {
  return sortRemitosByFechaDesc(JSON.parse(JSON.stringify(FALLBACK_REMITOS)));
}
