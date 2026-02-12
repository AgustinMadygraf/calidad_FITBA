import { FALLBACK_REMITOS } from "../config.js";
import { normalizeRemitosPayload } from "../domain/mappers/remitoMapper.js";

export async function loadRemitosWithFallback(
  remitoRepository,
  { fallbackRemitos = FALLBACK_REMITOS } = {}
) {
  try {
    const items = await remitoRepository.list();
    return { items, usedFallback: false };
  } catch (error) {
    const fallback = normalizeRemitosPayload(
      JSON.parse(JSON.stringify(fallbackRemitos))
    );
    return { items: fallback, usedFallback: true, error };
  }
}
