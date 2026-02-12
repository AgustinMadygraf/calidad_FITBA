export async function loadListaPrecios(listaPrecioRepository) {
  const items = await listaPrecioRepository.list();
  return { items };
}
