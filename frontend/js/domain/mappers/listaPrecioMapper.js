export function normalizeListaPreciosPayload(payload) {
  const rawItems = Array.isArray(payload?.items)
    ? payload.items
    : Array.isArray(payload)
      ? payload
      : [];
  return rawItems.map((item) =>
    item && typeof item === "object" ? { ...item } : item
  );
}
