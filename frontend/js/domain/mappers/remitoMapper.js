import { parseFechaToTimestamp } from "../dateUtils.js";
import { pickFirstDefined } from "./common.js";

function normalizeProductoRef(item) {
  const nestedProducto =
    item?.producto && typeof item.producto === "object" ? { ...item.producto } : {};
  const normalizedProductoId = pickFirstDefined(
    nestedProducto.ID,
    nestedProducto.id,
    item?.productoId,
    item?.productoid
  );

  if (normalizedProductoId !== null) {
    if (nestedProducto.ID === undefined || nestedProducto.ID === null) {
      nestedProducto.ID = normalizedProductoId;
    }
    if (nestedProducto.id === undefined || nestedProducto.id === null) {
      nestedProducto.id = normalizedProductoId;
    }
  }

  return nestedProducto;
}

function toItemVM(item) {
  return {
    transaccionCVItemId: item?.transaccionCVItemId ?? null,
    transaccionId: item?.transaccionId ?? null,
    producto: normalizeProductoRef(item),
    descripcion: item?.descripcion ?? "",
    cantidad: item?.cantidad ?? null,
    precio: item?.precio ?? null
  };
}

export function toRemitoVM(remito) {
  const items = Array.isArray(remito?.transaccionProductoItem)
    ? remito.transaccionProductoItem
    : [];

  return {
    transaccionId: remito?.transaccionId ?? null,
    numeroRemito: remito?.numeroRemito ?? "",
    fecha: remito?.fecha ?? "",
    observacion: remito?.observacion ?? "",
    clienteId: remito?.clienteId ?? null,
    comisionVendedor: remito?.comisionVendedor ?? null,
    depositoId: remito?.depositoId ?? null,
    circuitoContableId: remito?.circuitoContableId ?? null,
    transaccionProductoItem: items.map(toItemVM)
  };
}

export function sortRemitosByFechaDesc(remitos) {
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

export function normalizeRemitosPayload(payload) {
  const rawItems = Array.isArray(payload?.items)
    ? payload.items
    : Array.isArray(payload)
      ? payload
      : [];
  return sortRemitosByFechaDesc(rawItems.map(toRemitoVM));
}
