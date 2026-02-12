export const MODES = {
  NONE: "none",
  REMITO: "remito",
  CLIENTE: "cliente",
  PRODUCTO: "producto",
  LISTA_PRECIO: "listaPrecio",
  COMPROBANTE_VENTA: "comprobanteVenta"
};

const ALLOWED_TRANSITIONS = {
  [MODES.NONE]: [
    MODES.NONE,
    MODES.REMITO,
    MODES.LISTA_PRECIO,
    MODES.COMPROBANTE_VENTA
  ],
  [MODES.REMITO]: [
    MODES.REMITO,
    MODES.CLIENTE,
    MODES.PRODUCTO,
    MODES.NONE,
    MODES.LISTA_PRECIO,
    MODES.COMPROBANTE_VENTA
  ],
  [MODES.CLIENTE]: [
    MODES.CLIENTE,
    MODES.REMITO,
    MODES.NONE,
    MODES.LISTA_PRECIO,
    MODES.COMPROBANTE_VENTA
  ],
  [MODES.PRODUCTO]: [
    MODES.PRODUCTO,
    MODES.REMITO,
    MODES.NONE,
    MODES.LISTA_PRECIO,
    MODES.COMPROBANTE_VENTA
  ],
  [MODES.LISTA_PRECIO]: [
    MODES.LISTA_PRECIO,
    MODES.NONE,
    MODES.REMITO,
    MODES.COMPROBANTE_VENTA
  ],
  [MODES.COMPROBANTE_VENTA]: [
    MODES.COMPROBANTE_VENTA,
    MODES.NONE,
    MODES.REMITO,
    MODES.LISTA_PRECIO
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
  if (mode === MODES.COMPROBANTE_VENTA) {
    return MODES.COMPROBANTE_VENTA;
  }
  if (mode === MODES.NONE) {
    return MODES.NONE;
  }
  return MODES.REMITO;
}

export function isRemitoFlow(mode) {
  return mode === MODES.REMITO || mode === MODES.CLIENTE || mode === MODES.PRODUCTO;
}
