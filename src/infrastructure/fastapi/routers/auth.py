import base64
import hashlib
import json
import os
import secrets
import time
import uuid
from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from src.shared.config import get_frontend_cors_origins
from src.shared.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

_SESSION_COOKIE_NAME = "xubio_session"
_DEFAULT_SAMESITE = "lax"
_DEFAULT_TTL_SECONDS = 60 * 60 * 8
_DEFAULT_OIDC_TX_TTL_SECONDS = 60 * 10


@dataclass
class _SessionData:
    user: Dict[str, Any]
    expires_at: float


@dataclass
class _OidcTxData:
    redirect_path: str
    nonce: str
    code_verifier: str
    expires_at: float


_SESSIONS: Dict[str, _SessionData] = {}
_OIDC_TX: Dict[str, _OidcTxData] = {}


def _is_true(raw: str) -> bool:
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _cookie_secure() -> bool:
    raw = os.getenv("AUTH_COOKIE_SECURE", "").strip()
    if raw:
        return _is_true(raw)
    return _is_true(os.getenv("IS_PROD", "false"))


def _cookie_samesite() -> str:
    raw = os.getenv("AUTH_COOKIE_SAMESITE", "").strip().lower()
    if raw in {"lax", "strict", "none"}:
        return raw
    if _is_true(os.getenv("IS_PROD", "false")):
        return "none"
    return _DEFAULT_SAMESITE


def _cookie_max_age() -> int:
    raw = os.getenv("AUTH_SESSION_TTL_SECONDS", "").strip()
    if not raw:
        return _DEFAULT_TTL_SECONDS
    try:
        parsed = int(raw)
    except ValueError:
        return _DEFAULT_TTL_SECONDS
    if parsed <= 0:
        return _DEFAULT_TTL_SECONDS
    return parsed


def _authorization_endpoint() -> str:
    return os.getenv(
        "OIDC_AUTHORIZATION_ENDPOINT",
        "https://accounts.google.com/o/oauth2/v2/auth",
    ).strip()


def _token_endpoint() -> str:
    return os.getenv("OIDC_TOKEN_ENDPOINT", "https://oauth2.googleapis.com/token").strip()


def _tokeninfo_endpoint() -> str:
    return os.getenv(
        "OIDC_TOKENINFO_ENDPOINT", "https://oauth2.googleapis.com/tokeninfo"
    ).strip()


def _validate_redirect_path(redirect_path: str) -> str:
    path = (redirect_path or "").strip()
    if not path:
        return "/"
    if not path.startswith("/"):
        raise HTTPException(status_code=400, detail="redirectPath invalido")
    if path.startswith("//"):
        raise HTTPException(status_code=400, detail="redirectPath invalido")
    if "://" in path:
        raise HTTPException(status_code=400, detail="redirectPath invalido")
    return path


def _cleanup_expired_sessions(now: Optional[float] = None) -> None:
    now = now if now is not None else time.time()
    expired = [sid for sid, data in _SESSIONS.items() if data.expires_at <= now]
    for sid in expired:
        _SESSIONS.pop(sid, None)


def _cleanup_expired_oidc_tx(now: Optional[float] = None) -> None:
    now = now if now is not None else time.time()
    expired = [state for state, data in _OIDC_TX.items() if data.expires_at <= now]
    for state in expired:
        _OIDC_TX.pop(state, None)


def _build_login_url(redirect_path: str) -> str:
    # Backend generates state + PKCE challenge to keep OIDC bootstrap server-side.
    _cleanup_expired_oidc_tx()
    state = secrets.token_urlsafe(24)
    nonce = secrets.token_urlsafe(24)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode("ascii").rstrip("=")
    _OIDC_TX[state] = _OidcTxData(
        redirect_path=redirect_path,
        nonce=nonce,
        code_verifier=code_verifier,
        expires_at=time.time() + _DEFAULT_OIDC_TX_TTL_SECONDS,
    )
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip() or "missing-google-client-id"
    redirect_uri = os.getenv(
        "OIDC_REDIRECT_URI",
        "http://127.0.0.1:8000/auth/callback/google",
    ).strip()
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": redirect_uri,
        "state": state,
        "nonce": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "consent",
        "access_type": "offline",
    }
    return f"{_authorization_endpoint()}?{urlencode(params)}"


def _session_payload(request: Request) -> Dict[str, Any]:
    _cleanup_expired_sessions()
    sid = request.cookies.get(_SESSION_COOKIE_NAME, "")
    if not sid:
        return {"authenticated": False, "user": None}
    session = _SESSIONS.get(sid)
    if session is None:
        return {"authenticated": False, "user": None}
    return {"authenticated": True, "user": session.user}


def _request_id(request: Request) -> str:
    return request.headers.get("x-request-id", "").strip() or str(uuid.uuid4())


def _enforce_csrf_origin(request: Request) -> None:
    origin = request.headers.get("origin", "").strip()
    if not origin:
        raise HTTPException(status_code=403, detail="Origen requerido")
    allowed = set(get_frontend_cors_origins())
    if origin not in allowed:
        raise HTTPException(status_code=403, detail="Origen no permitido")


@router.get("/auth/session")
def auth_session(request: Request) -> Dict[str, Any]:
    req_id = _request_id(request)
    payload = _session_payload(request)
    logger.info(
        "event=auth.session.read correlation_id=%s authenticated=%s",
        req_id,
        payload["authenticated"],
    )
    return payload


@router.post("/auth/login/google")
def auth_login_google(request: Request, payload: Dict[str, Any]) -> Dict[str, str]:
    _enforce_csrf_origin(request)
    req_id = _request_id(request)
    redirect_path = _validate_redirect_path(str(payload.get("redirectPath", "/")))
    logger.info(
        "event=auth.login.start correlation_id=%s redirect_path=%s",
        req_id,
        redirect_path,
    )
    return {"url": _build_login_url(redirect_path)}


def _parse_jwt_payload_without_verification(token: str) -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=400, detail="id_token invalido")
    payload_b64 = parts[1]
    padded = payload_b64 + "=" * (-len(payload_b64) % 4)
    try:
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail="id_token invalido") from exc


def _exchange_code_for_tokens(code: str, code_verifier: str) -> Dict[str, Any]:
    client_id = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv(
        "OIDC_REDIRECT_URI",
        "http://127.0.0.1:8000/auth/callback/google",
    ).strip()
    if not client_id or not client_secret:
        raise HTTPException(
            status_code=500, detail="GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET faltantes"
        )
    resp = httpx.post(
        _token_endpoint(),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier,
        },
        timeout=10.0,
    )
    if resp.status_code >= 400:
        raise HTTPException(status_code=500, detail="Error al intercambiar codigo OIDC")
    data = resp.json()
    if "id_token" not in data:
        raise HTTPException(status_code=500, detail="Respuesta OIDC sin id_token")
    return data


def _validate_id_token_claims(id_token: str, expected_nonce: str) -> Dict[str, Any]:
    claims = _parse_jwt_payload_without_verification(id_token)
    now = int(time.time())
    iss = str(claims.get("iss", ""))
    aud = str(claims.get("aud", ""))
    nonce = str(claims.get("nonce", ""))
    exp = int(claims.get("exp", 0))
    expected_aud = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    if iss not in {"https://accounts.google.com", "accounts.google.com"}:
        raise HTTPException(status_code=400, detail="id_token.iss invalido")
    if not expected_aud or aud != expected_aud:
        raise HTTPException(status_code=400, detail="id_token.aud invalido")
    if exp <= now:
        raise HTTPException(status_code=400, detail="id_token expirado")
    if nonce != expected_nonce:
        raise HTTPException(status_code=400, detail="id_token.nonce invalido")
    # Verify signature/issuer/audience through Google tokeninfo endpoint.
    tokeninfo = httpx.get(_tokeninfo_endpoint(), params={"id_token": id_token}, timeout=10.0)
    if tokeninfo.status_code >= 400:
        raise HTTPException(status_code=400, detail="id_token no valido por proveedor")
    return claims


@router.get("/auth/callback/google")
def auth_callback_google(request: Request, code: str = "", state: str = "") -> Response:
    req_id = _request_id(request)
    _cleanup_expired_oidc_tx()
    if not code or not state:
        logger.warning(
            "event=auth.login.callback.failure correlation_id=%s reason=invalid_callback",
            req_id,
        )
        raise HTTPException(status_code=400, detail="Callback OIDC invalido")
    tx = _OIDC_TX.pop(state, None)
    if tx is None:
        logger.warning(
            "event=auth.login.callback.failure correlation_id=%s reason=invalid_state",
            req_id,
        )
        raise HTTPException(status_code=400, detail="state invalido o expirado")
    tokens = _exchange_code_for_tokens(code, tx.code_verifier)
    claims = _validate_id_token_claims(tokens["id_token"], tx.nonce)
    sid = secrets.token_urlsafe(32)
    _SESSIONS[sid] = _SessionData(
        user={
            "id": str(claims.get("sub", "")),
            "email": str(claims.get("email", "")),
            "name": str(claims.get("name", "")),
            "pictureUrl": str(claims.get("picture", "")),
        },
        expires_at=time.time() + _cookie_max_age(),
    )
    safe_redirect = _validate_redirect_path(tx.redirect_path)
    response = RedirectResponse(url=safe_redirect, status_code=302)
    response.set_cookie(
        key=_SESSION_COOKIE_NAME,
        value=sid,
        max_age=_cookie_max_age(),
        httponly=True,
        secure=_cookie_secure(),
        samesite=_cookie_samesite(),
        path="/",
    )
    logger.info(
        "event=auth.login.callback.success correlation_id=%s user_id=%s redirect_path=%s",
        req_id,
        _SESSIONS[sid].user.get("id", ""),
        safe_redirect,
    )
    return response


@router.post("/auth/logout")
def auth_logout(request: Request, response: Response) -> Dict[str, bool]:
    _enforce_csrf_origin(request)
    req_id = _request_id(request)
    sid = request.cookies.get(_SESSION_COOKIE_NAME, "")
    if sid:
        _SESSIONS.pop(sid, None)
    response.delete_cookie(
        key=_SESSION_COOKIE_NAME,
        path="/",
        secure=_cookie_secure(),
        httponly=True,
        samesite=_cookie_samesite(),
    )
    logger.info("event=auth.logout correlation_id=%s had_session=%s", req_id, bool(sid))
    return {"ok": True}
