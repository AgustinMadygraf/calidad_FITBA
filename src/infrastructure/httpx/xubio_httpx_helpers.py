"""
Path: src/infrastructure/httpx/xubio_httpx_helpers.py
"""

from typing import Any, Dict, List

import httpx

from ...use_cases.errors import ExternalServiceError


def _safe_xubio_error_message(payload: Dict[str, Any]) -> str:
    message = payload.get("message") or payload.get("description") or payload.get("error")
    if isinstance(message, str) and message.strip():
        return message.strip()
    return "Error del servicio externo"


def _resolve_http_status(resp_status: int, payload: Dict[str, Any]) -> int:
    code_response = payload.get("codeResponse")
    if isinstance(code_response, str) and code_response.isdigit():
        value = int(code_response)
        if 400 <= value <= 599:
            return value
    if isinstance(code_response, int) and 400 <= code_response <= 599:
        return code_response
    if isinstance(payload.get("error"), str) and payload.get("error") == "invalid_request":
        combined_message = " ".join(
            str(part)
            for part in (payload.get("message"), payload.get("description"))
            if isinstance(part, str)
        ).lower()
        if "no existe" in combined_message or "not found" in combined_message:
            return 404
        return 400
    return resp_status if 400 <= resp_status <= 599 else 502


def raise_for_status(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        payload: Dict[str, Any] = {}
        try:
            raw = resp.json()
            if isinstance(raw, dict):
                payload = raw
        except Exception:
            payload = {}

        if payload:
            status = _resolve_http_status(resp.status_code, payload)
            message = _safe_xubio_error_message(payload)
            raise ExternalServiceError(
                f"Xubio error {status}: {message}", status_code=status
            )

        body = (resp.text or "").strip()
        short_body = body[:200] if body else "sin detalle"
        status = resp.status_code if 400 <= resp.status_code <= 599 else 502
        raise ExternalServiceError(
            f"Xubio error {status}: {short_body}",
            status_code=status,
        )


def extract_list(resp: httpx.Response, *, label: str) -> List[Dict[str, Any]]:
    raise_for_status(resp)
    payload = resp.json()
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        return payload["items"]
    raise ExternalServiceError(f"Respuesta inesperada al listar {label}")
