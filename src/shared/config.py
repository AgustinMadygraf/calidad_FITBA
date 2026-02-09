import base64
import os


def build_xubio_token() -> str:
    """
    Genera un token base64 a partir de variables de entorno.
    - Usa XUBIO_CLIENT_ID.
    - Usa XUBIO_SECRET_ID si existe; si no, intenta XUBIO_CLIENT_SECRET.
    - Si no hay secreto, reutiliza XUBIO_CLIENT_ID.
    """
    client_id = os.getenv("XUBIO_CLIENT_ID", "")
    client_secret = os.getenv("XUBIO_SECRET_ID")
    if client_secret is None:
        client_secret = os.getenv("XUBIO_CLIENT_SECRET")
    if client_secret is None:
        client_secret = os.getenv("XUBIO_CLIENT_ID", "")

    raw = f"{client_id}:{client_secret}"
    return base64.b64encode(raw.encode("utf-8")).decode("ascii")
