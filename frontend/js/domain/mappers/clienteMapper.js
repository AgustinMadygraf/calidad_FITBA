import { normalizeObject, normalizeSimpleItem, pickFirstDefined } from "./common.js";

export function toClienteVM(cliente) {
  return {
    cliente_id: pickFirstDefined(cliente?.cliente_id, cliente?.clienteId),
    nombre: cliente?.nombre ?? "",
    razonSocial: cliente?.razonSocial ?? "",
    identificacionTributaria: normalizeSimpleItem(cliente?.identificacionTributaria),
    categoriaFiscal: normalizeSimpleItem(cliente?.categoriaFiscal),
    cuit: cliente?.cuit ?? "",
    CUIT: cliente?.CUIT ?? "",
    responsabilidadOrganizacionItem: Array.isArray(
      cliente?.responsabilidadOrganizacionItem
    )
      ? [...cliente.responsabilidadOrganizacionItem]
      : [],
    esclienteextranjero: cliente?.esclienteextranjero ?? null,
    esProveedor: cliente?.esProveedor ?? null,
    direccion: cliente?.direccion ?? "",
    email: cliente?.email ?? "",
    telefono: cliente?.telefono ?? "",
    provincia: normalizeObject(cliente?.provincia),
    pais: normalizeSimpleItem(cliente?.pais),
    cuentaVenta_id: normalizeSimpleItem(cliente?.cuentaVenta_id),
    cuentaCompra_id: normalizeSimpleItem(cliente?.cuentaCompra_id),
    usrCode: cliente?.usrCode ?? cliente?.usrcode ?? "",
    descripcion: cliente?.descripcion ?? ""
  };
}
