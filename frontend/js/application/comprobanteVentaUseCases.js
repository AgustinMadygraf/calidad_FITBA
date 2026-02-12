export async function loadComprobantesVenta(comprobanteVentaRepository) {
  const items = await comprobanteVentaRepository.list();
  return { items };
}
