import pytest
from fastapi import HTTPException

from src.infrastructure.fastapi.runtime_policy import (
    ensure_debug_allowed,
    ensure_write_allowed,
)


def test_ensure_write_allowed_blocks_in_non_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    with pytest.raises(HTTPException) as exc_info:
        ensure_write_allowed()
    assert exc_info.value.status_code == 403


def test_ensure_write_allowed_allows_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    ensure_write_allowed()


def test_ensure_debug_allowed_blocks_in_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "true")
    with pytest.raises(HTTPException) as exc_info:
        ensure_debug_allowed()
    assert exc_info.value.status_code == 404


def test_ensure_debug_allowed_allows_in_non_prod(monkeypatch):
    monkeypatch.setenv("IS_PROD", "false")
    ensure_debug_allowed()
