function padTwoDigits(value) {
  return String(value).padStart(2, "0");
}

export function formatFechaDDMMYY(value) {
  if (value === undefined || value === null) {
    return "";
  }

  const raw = String(value).trim();
  if (!raw) {
    return "";
  }

  const isoMatch = raw.match(/^(\d{4})-(\d{1,2})-(\d{1,2})(?:[T ].*)?$/);
  if (isoMatch) {
    const year = isoMatch[1].slice(-2);
    const month = padTwoDigits(isoMatch[2]);
    const day = padTwoDigits(isoMatch[3]);
    return `${day}-${month}-${year}`;
  }

  const slashMatch = raw.match(
    /^(\d{1,2})\/(\d{1,2})\/(\d{2,4})(?:[ T]\d{1,2}:\d{2}(?::\d{2})?)?$/
  );
  if (slashMatch) {
    const day = padTwoDigits(slashMatch[1]);
    const month = padTwoDigits(slashMatch[2]);
    const year = slashMatch[3].slice(-2);
    return `${day}-${month}-${year}`;
  }

  const parsed = Date.parse(raw.replace(/\s+/g, " "));
  if (!Number.isFinite(parsed)) {
    return raw;
  }

  const date = new Date(parsed);
  const day = padTwoDigits(date.getUTCDate());
  const month = padTwoDigits(date.getUTCMonth() + 1);
  const year = String(date.getUTCFullYear()).slice(-2);
  return `${day}-${month}-${year}`;
}

export function parseFechaToTimestamp(fecha) {
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
