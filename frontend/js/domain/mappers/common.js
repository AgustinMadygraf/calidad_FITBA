function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

export function pickFirstDefined(...values) {
  for (const value of values) {
    if (value !== undefined && value !== null) {
      return value;
    }
  }
  return null;
}

export function normalizeSimpleItem(value) {
  if (!isPlainObject(value)) {
    return null;
  }

  return {
    ID: pickFirstDefined(value.ID, value.id),
    nombre: value.nombre ?? "",
    codigo: value.codigo ?? "",
    id: pickFirstDefined(value.id, value.ID)
  };
}

export function normalizeObject(value) {
  if (!isPlainObject(value)) {
    return null;
  }
  return { ...value };
}
