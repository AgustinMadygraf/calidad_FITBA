"""
Path: src/infrastructure/httpx/xubio_crud_helpers.py
"""

from typing import Any, Dict, List, Optional

import httpx

from ...use_cases.errors import ExternalServiceError
from .token_client import request_with_token
from .xubio_httpx_helpers import extract_list, raise_for_status


def list_items(
    *, url: str, timeout: float, label: str, logger: Any
) -> List[Dict[str, Any]]:
    try:
        resp = request_with_token("GET", url, timeout=timeout)
        logger.info("Xubio GET %s -> %s", url, resp.status_code)
        items = extract_list(resp, label=label)
        logger.info("Xubio lista %s: %d items", label, len(items))
        return items
    except httpx.HTTPError as exc:
        raise ExternalServiceError(str(exc)) from exc


def get_item(*, url: str, timeout: float, logger: Any) -> Optional[Dict[str, Any]]:
    try:
        resp = request_with_token("GET", url, timeout=timeout)
        logger.info("Xubio GET %s -> %s", url, resp.status_code)
        if resp.status_code == 404:
            return None
        raise_for_status(resp)
        return resp.json()
    except httpx.HTTPError as exc:
        raise ExternalServiceError(str(exc)) from exc


def create_item(
    *, url: str, timeout: float, data: Dict[str, Any], logger: Any
) -> Dict[str, Any]:
    try:
        resp = request_with_token("POST", url, timeout=timeout, json=data)
        logger.info("Xubio POST %s -> %s", url, resp.status_code)
        raise_for_status(resp)
        return resp.json()
    except httpx.HTTPError as exc:
        raise ExternalServiceError(str(exc)) from exc


def update_item(
    *, url: str, timeout: float, data: Dict[str, Any], logger: Any
) -> Optional[Dict[str, Any]]:
    try:
        resp = request_with_token("PUT", url, timeout=timeout, json=data)
        logger.info("Xubio PUT %s -> %s", url, resp.status_code)
        if resp.status_code == 404:
            return None
        raise_for_status(resp)
        return resp.json()
    except httpx.HTTPError as exc:
        raise ExternalServiceError(str(exc)) from exc


def delete_item(*, url: str, timeout: float, logger: Any) -> bool:
    try:
        resp = request_with_token("DELETE", url, timeout=timeout)
        logger.info("Xubio DELETE %s -> %s", url, resp.status_code)
        if resp.status_code == 404:
            return False
        raise_for_status(resp)
        return True
    except httpx.HTTPError as exc:
        raise ExternalServiceError(str(exc)) from exc
