from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from ...shared.id_mapping import extract_int_id, match_any_id
from .cache_provider import CacheProvider


class XubioCachedCrudGatewayBase:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        list_cache_ttl: float,
        path: str,
        list_label: str,
        detail_label: str,
        id_keys: Sequence[str],
        logger: Any,
        list_cache_provider: CacheProvider,
        item_cache_provider: Optional[CacheProvider] = None,
        prefer_list_lookup_before_detail: bool = False,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._list_cache_ttl = max(0.0, float(list_cache_ttl))
        self._path = path
        self._list_label = list_label
        self._detail_label = detail_label
        self._id_keys = tuple(id_keys)
        self._logger = logger
        self._list_cache_provider = list_cache_provider
        self._item_cache_provider = item_cache_provider
        self._prefer_list_lookup_before_detail = prefer_list_lookup_before_detail

    def _url(self, path: str) -> str:
        return f"{self._base_url}{path}"

    def list(self) -> List[Dict[str, Any]]:
        cached = self._get_cached_list()
        if cached is not None:
            return cached
        items = self._fetch_list_remote()
        self._store_cache(items)
        return items

    def get(self, resource_id: int) -> Optional[Dict[str, Any]]:
        cached_item = self._get_cached_item(resource_id)
        if cached_item is not None:
            self._logger.info(
                "Xubio %s detalle: cache hit (%s)", self._detail_label, resource_id
            )
            return cached_item

        if self._prefer_list_lookup_before_detail:
            cached = self._get_cached_list()
            if cached is not None:
                cached_match = self._find_in_items(cached, resource_id)
                if cached_match is not None:
                    self._store_item_cache(resource_id, cached_match)
                    return cached_match

        item = self._fetch_detail_remote(resource_id)
        if item is not None:
            self._store_item_cache(resource_id, item)
        return item

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        created = self._create_remote(data)
        self._clear_list_cache()
        self._clear_item_cache()
        return created

    def update(self, resource_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        updated = self._update_remote(resource_id, data)
        self._clear_list_cache()
        self._clear_item_cache(resource_id)
        return updated

    def patch(self, resource_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        patched = self._patch_remote(resource_id, data)
        self._clear_list_cache()
        self._clear_item_cache(resource_id)
        return patched

    def delete(self, resource_id: int) -> bool:
        deleted = self._delete_remote(resource_id)
        if deleted:
            self._clear_list_cache()
            self._clear_item_cache(resource_id)
        return deleted

    def _fallback_get_from_list(self, resource_id: int) -> Optional[Dict[str, Any]]:
        return self._find_in_items(self.list(), resource_id)

    def _find_in_items(
        self, items: List[Dict[str, Any]], resource_id: int
    ) -> Optional[Dict[str, Any]]:
        for item in items:
            if match_any_id(item, resource_id, self._id_keys):
                return item
        return None

    def _get_cached_list(self) -> Optional[List[Dict[str, Any]]]:
        cached = self._list_cache_provider.get(self._path, ttl=self._list_cache_ttl)
        if cached is not None:
            self._logger.info(
                "Xubio lista %s: cache hit (%d items)", self._list_label, len(cached)
            )
        return cached

    def _store_cache(self, items: List[Dict[str, Any]]) -> None:
        self._list_cache_provider.set(self._path, items, ttl=self._list_cache_ttl)
        for item in items:
            item_id = extract_int_id(item, self._id_keys)
            if item_id is not None:
                self._store_item_cache(item_id, item)

    def _clear_list_cache(self) -> None:
        self._list_cache_provider.delete(self._path)

    def _get_cached_item(self, resource_id: int) -> Optional[Dict[str, Any]]:
        if self._item_cache_provider is None:
            return None
        return self._item_cache_provider.get(
            self._item_cache_key(resource_id),
            ttl=self._list_cache_ttl,
        )

    def _store_item_cache(self, resource_id: int, item: Optional[Dict[str, Any]]) -> None:
        if self._item_cache_provider is None or item is None:
            return
        self._item_cache_provider.set(
            self._item_cache_key(resource_id),
            item,
            ttl=self._list_cache_ttl,
        )

    def _clear_item_cache(self, resource_id: Optional[int] = None) -> None:
        if self._item_cache_provider is None:
            return
        if resource_id is None:
            self._item_cache_provider.clear()
            return
        self._item_cache_provider.delete(self._item_cache_key(resource_id))

    def _item_cache_key(self, resource_id: int) -> str:
        return f"{self._path}/{resource_id}"

    def _fetch_list_remote(self) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def _fetch_detail_remote(self, resource_id: int) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def _create_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def _update_remote(
        self, resource_id: int, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def _patch_remote(self, resource_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def _delete_remote(self, resource_id: int) -> bool:
        raise NotImplementedError
