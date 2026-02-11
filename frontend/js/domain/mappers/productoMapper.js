import { normalizeSimpleItem, pickFirstDefined } from "./common.js";

export function toProductoVM(producto) {
  return {
    productoid: pickFirstDefined(
      producto?.productoid,
      producto?.productoID,
      producto?.id,
      producto?.ID
    ),
    nombre: producto?.nombre ?? "",
    codigo: producto?.codigo ?? "",
    usrcode: producto?.usrcode ?? producto?.usrCode ?? "",
    codigoBarra: producto?.codigoBarra ?? "",
    unidadMedida: normalizeSimpleItem(producto?.unidadMedida),
    categoria: producto?.categoria ?? null,
    stockNegativo: producto?.stockNegativo ?? null,
    tasaIva: normalizeSimpleItem(producto?.tasaIva),
    cuentaContable: normalizeSimpleItem(producto?.cuentaContable),
    catFormIVA2002: producto?.catFormIVA2002 ?? null,
    precioUltCompra: producto?.precioUltCompra ?? null,
    activo: producto?.activo ?? null,
    sincronizaStock: producto?.sincronizaStock ?? null
  };
}
