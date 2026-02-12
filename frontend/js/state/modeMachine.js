export const MODES = {
  NONE: "none",
  REMITO: "remito",
  CLIENTE: "cliente",
  PRODUCTO: "producto",
  LISTA_PRECIO: "listaPrecio"
};

const ALLOWED_TRANSITIONS = {
  [MODES.NONE]: [MODES.NONE, MODES.REMITO, MODES.LISTA_PRECIO],
  [MODES.REMITO]: [
    MODES.REMITO,
    MODES.CLIENTE,
    MODES.PRODUCTO,
    MODES.NONE,
    MODES.LISTA_PRECIO
  ],
  [MODES.CLIENTE]: [
    MODES.CLIENTE,
    MODES.REMITO,
    MODES.NONE,
    MODES.LISTA_PRECIO
  ],
  [MODES.PRODUCTO]: [
    MODES.PRODUCTO,
    MODES.REMITO,
    MODES.NONE,
    MODES.LISTA_PRECIO
  ],
  [MODES.LISTA_PRECIO]: [
    MODES.LISTA_PRECIO,
    MODES.NONE,
    MODES.REMITO
  ]
};

export function transitionMode(current, next) {
  if (!Object.values(MODES).includes(next)) {
    console.warn("Modo invalido:", next);
    return current;
  }

  const allowed = ALLOWED_TRANSITIONS[current] || [];
  if (!allowed.includes(next)) {
    console.warn(`Transicion de modo no esperada: ${current} -> ${next}`);
  }

  return next;
}

export function getActiveModule(mode) {
  if (mode === MODES.LISTA_PRECIO) {
    return MODES.LISTA_PRECIO;
  }
  if (mode === MODES.NONE) {
    return MODES.NONE;
  }
  return MODES.REMITO;
}

export function isRemitoFlow(mode) {
  return mode === MODES.REMITO || mode === MODES.CLIENTE || mode === MODES.PRODUCTO;
}
