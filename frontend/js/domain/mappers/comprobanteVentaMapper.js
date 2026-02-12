import { parseFechaToTimestamp } from "../dateUtils.js";
import { pickFirstDefined } from "./common.js";

function normalizeNombreVendedor(vendedor) {
  const nombre = vendedor?.nombre ?? "";
  const apellido = vendedor?.apellido ?? "";
  return `${nombre} ${apellido}`.trim();
}

function toComprobanteVentaVM(item) {
  const cliente =
    item?.cliente && typeof item.cliente === "object" ? { ...item.cliente } : null;
  const vendedor =
    item?.vendedor && typeof item.vendedor === "object" ? { ...item.vendedor } : null;

  return {
    transaccionid: pickFirstDefined(
      item?.transaccionid,
      item?.transaccionId,
      item?.id,
      item?.ID
    ),
    nombre: item?.nombre ?? "",
    fecha: item?.fecha ?? "",
    externalId: pickFirstDefined(item?.externalId, item?.externalid) ?? "",
    importetotal: pickFirstDefined(
      item?.importetotal,
      item?.importeTotal,
      item?.importeMonPrincipal
    ),
    clienteNombre: cliente?.nombre ?? "",
    vendedorNombre: normalizeNombreVendedor(vendedor),
    cliente,
    vendedor
  };
}

function sortComprobantesByFechaDesc(comprobantes) {
  return [...comprobantes].sort((left, right) => {
    const timestampDifference =
      parseFechaToTimestamp(right?.fecha) - parseFechaToTimestamp(left?.fecha);
    if (timestampDifference !== 0) {
      return timestampDifference;
    }

    const leftId = Number(left?.transaccionid);
    const rightId = Number(right?.transaccionid);
    if (Number.isFinite(leftId) && Number.isFinite(rightId) && leftId !== rightId) {
      return rightId - leftId;
    }

    return 0;
  });
}

export function normalizeComprobantesVentaPayload(payload) {
  const rawItems = Array.isArray(payload?.items)
    ? payload.items
    : Array.isArray(payload)
      ? payload
      : [];
  return sortComprobantesByFechaDesc(rawItems.map(toComprobanteVentaVM));
}
