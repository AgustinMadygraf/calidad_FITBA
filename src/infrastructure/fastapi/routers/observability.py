from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from ....shared.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

ALLOWED_EVENT_TYPES = {
    "http_request",
    "route_navigation",
    "page_load",
    "frontend_error",
}
ALLOWED_LEVELS = {"info", "warn", "error"}

MAX_EVENT_BODY_BYTES = 32 * 1024
MAX_STACK_BYTES = 8 * 1024
RATE_LIMIT_MAX_REQUESTS = 120
RATE_LIMIT_WINDOW_SECONDS = 60.0
MAX_STORED_EVENTS = 20_000

_LOCK = Lock()
_NEXT_EVENT_ID = 1
_EVENTS: List[Dict[str, Any]] = []
_RATE_LIMIT_STATE: Dict[str, Tuple[float, int]] = {}


@router.post("/observability/events")
async def ingest_event(request: Request) -> JSONResponse:
    request_id = str(uuid.uuid4())
    client_ip = _get_client_ip(request)

    try:
        content_type = request.headers.get("content-type", "")
        if not _is_json_content_type(content_type):
            return _reject(
                status_code=415,
                request_id=request_id,
                client_ip=client_ip,
                reason="content_type_invalido",
                detail="Content-Type debe ser application/json.",
            )

        if _is_rate_limited(client_ip):
            return _reject(
                status_code=429,
                request_id=request_id,
                client_ip=client_ip,
                reason="rate_limit",
                detail="Rate limit excedido. Intenta nuevamente en breve.",
            )

        body = await request.body()
        if not body:
            return _reject(
                status_code=400,
                request_id=request_id,
                client_ip=client_ip,
                reason="body_vacio",
                detail="Body JSON requerido.",
            )
        if len(body) > MAX_EVENT_BODY_BYTES:
            return _reject(
                status_code=413,
                request_id=request_id,
                client_ip=client_ip,
                reason="body_demasiado_grande",
                detail=f"Body excede {MAX_EVENT_BODY_BYTES} bytes.",
            )

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return _reject(
                status_code=400,
                request_id=request_id,
                client_ip=client_ip,
                reason="json_invalido",
                detail="JSON invalido.",
            )

        validation_error = _validate_payload(payload)
        if validation_error is not None:
            return _reject(
                status_code=400,
                request_id=request_id,
                client_ip=client_ip,
                reason="contrato_invalido",
                detail=validation_error,
            )

        event = _normalize_for_storage(payload, request_id=request_id)
        _persist_event(event)

        logger.info(
            "observability accepted request_id=%s client_ip=%s type=%s level=%s",
            request_id,
            client_ip,
            event["eventType"],
            event["level"],
        )
        return JSONResponse(
            status_code=202,
            content={
                "status": "accepted",
                "requestId": request_id,
            },
        )
    except Exception as exc:  # pragma: no cover - safety net
        logger.exception(
            "observability internal_error request_id=%s client_ip=%s err=%s",
            request_id,
            client_ip,
            exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error.", "requestId": request_id},
        )


def _reject(
    *,
    status_code: int,
    request_id: str,
    client_ip: str,
    reason: str,
    detail: str,
) -> JSONResponse:
    logger.warning(
        "observability rejected request_id=%s client_ip=%s status=%d reason=%s",
        request_id,
        client_ip,
        status_code,
        reason,
    )
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": detail,
            "requestId": request_id,
        },
    )


def _is_json_content_type(content_type: str) -> bool:
    return content_type.lower().startswith("application/json")


def _validate_payload(payload: Any) -> str | None:
    if not isinstance(payload, dict):
        return "El payload debe ser un objeto JSON."

    for field in ("type", "level", "timestamp", "context"):
        if field not in payload:
            return f"Falta campo requerido: {field}"

    event_type = payload["type"]
    if not isinstance(event_type, str) or event_type not in ALLOWED_EVENT_TYPES:
        return (
            "type invalido. Valores permitidos: http_request, route_navigation, "
            "page_load, frontend_error."
        )

    level = payload["level"]
    if not isinstance(level, str) or level not in ALLOWED_LEVELS:
        return "level invalido. Valores permitidos: info, warn, error."

    if not isinstance(payload["context"], dict):
        return "context debe ser un objeto JSON."

    timestamp = payload["timestamp"]
    if not isinstance(timestamp, str) or not _is_valid_utc_iso_timestamp(timestamp):
        return "timestamp invalido. Debe ser ISO-8601 UTC."

    return None


def _is_valid_utc_iso_timestamp(raw: str) -> bool:
    normalized = raw.strip()
    if not normalized:
        return False
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    if parsed.tzinfo is None:
        return False
    return parsed.utcoffset() == timedelta(0)


def _normalize_for_storage(
    payload: Dict[str, Any], *, request_id: str
) -> Dict[str, Any]:
    context = dict(payload["context"])

    if payload["type"] == "frontend_error":
        stack = context.get("stack")
        if isinstance(stack, str):
            context["stack"] = _truncate_utf8(stack, MAX_STACK_BYTES)

    return {
        "eventType": payload["type"],
        "level": payload["level"],
        "eventTimestamp": payload["timestamp"],
        "context": context,
        "requestId": request_id,
    }


def _truncate_utf8(value: str, max_bytes: int) -> str:
    raw = value.encode("utf-8")
    if len(raw) <= max_bytes:
        return value
    return raw[:max_bytes].decode("utf-8", errors="ignore")


def _persist_event(event: Dict[str, Any]) -> None:
    global _NEXT_EVENT_ID  # pylint: disable=global-statement
    now = datetime.now(timezone.utc).isoformat()
    with _LOCK:
        record = {
            "id": _NEXT_EVENT_ID,
            "receivedAt": now,
            "eventType": event["eventType"],
            "level": event["level"],
            "eventTimestamp": event["eventTimestamp"],
            "context": event["context"],
            "requestId": event["requestId"],
        }
        _NEXT_EVENT_ID += 1
        _EVENTS.append(record)
        if len(_EVENTS) > MAX_STORED_EVENTS:
            del _EVENTS[0 : len(_EVENTS) - MAX_STORED_EVENTS]


def _is_rate_limited(client_ip: str) -> bool:
    now = time.time()
    with _LOCK:
        _cleanup_rate_limit(now)
        window_start, count = _RATE_LIMIT_STATE.get(client_ip, (now, 0))
        if now - window_start >= RATE_LIMIT_WINDOW_SECONDS:
            window_start, count = now, 0
        count += 1
        _RATE_LIMIT_STATE[client_ip] = (window_start, count)
        return count > RATE_LIMIT_MAX_REQUESTS


def _cleanup_rate_limit(now: float) -> None:
    threshold = now - (2 * RATE_LIMIT_WINDOW_SECONDS)
    stale_keys = [
        key for key, (window_start, _count) in _RATE_LIMIT_STATE.items()
        if window_start < threshold
    ]
    for key in stale_keys:
        _RATE_LIMIT_STATE.pop(key, None)


def _get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").strip()
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _reset_observability_state_for_tests() -> None:
    global _NEXT_EVENT_ID  # pylint: disable=global-statement
    with _LOCK:
        _NEXT_EVENT_ID = 1
        _EVENTS.clear()
        _RATE_LIMIT_STATE.clear()


def _events_snapshot_for_tests() -> List[Dict[str, Any]]:
    with _LOCK:
        return [dict(item) for item in _EVENTS]
