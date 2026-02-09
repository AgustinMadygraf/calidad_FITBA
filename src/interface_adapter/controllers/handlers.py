from typing import Any, Dict, Optional

from ...use_cases import token_inspect


def root() -> Dict[str, str]:
    return {"status": "ok", "message": "Xubio-like API"}


def health() -> Dict[str, str]:
    return {"status": "ok"}


def terminal_execute(command: str) -> Dict[str, Any]:
    return {"status": "stub", "echo": command}


def sync_pull_product(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"status": "stub", "action": "pull", "entity": "product", "payload": payload}


def sync_push_product(payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"status": "stub", "action": "push", "entity": "product", "payload": payload}


def inspect_token() -> Dict[str, Any]:
    return token_inspect.execute()
