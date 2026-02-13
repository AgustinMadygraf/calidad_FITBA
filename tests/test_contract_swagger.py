import json
import re
from pathlib import Path
from typing import Dict, Iterable, Set

from src.infrastructure.fastapi.api import app

ALLOWED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
DOCS_PATH = Path(__file__).resolve().parents[1] / "docs" / "relevamiento_endpoints_xubio.md"
SWAGGER_PATH = Path(__file__).resolve().parents[1] / "docs" / "swagger.json"
IGNORED_PATHS = {
    "/docs",
    "/docs/oauth2-redirect",
    "/redoc",
    "/openapi.json",
}


def _normalize_path(path: str) -> str:
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    path = re.sub(r"\{[^}]+\}", "{param}", path)
    return path


def _load_swagger_methods() -> Dict[str, Set[str]]:
    data = json.loads(SWAGGER_PATH.read_text(encoding="utf-8"))
    result: Dict[str, Set[str]] = {}
    for raw_path, methods in data.get("paths", {}).items():
        norm_path = _normalize_path(raw_path)
        allowed: Set[str] = set()
        for method in methods.keys():
            upper = method.upper()
            if upper in ALLOWED_METHODS:
                allowed.add(upper)
        if allowed:
            result[norm_path] = allowed
    return result


def _load_allowed_extensions() -> Set[str]:
    if not DOCS_PATH.exists():
        return set()
    allowed: Set[str] = set()
    for line in DOCS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("- `"):
            continue
        match = re.match(r"- `([^`]+)`", line)
        if not match:
            continue
        allowed.add(_normalize_path(match.group(1)))
    return allowed


def _collect_local_routes() -> Dict[str, Set[str]]:
    routes: Dict[str, Set[str]] = {}
    for route in app.routes:
        if not hasattr(route, "methods"):
            continue
        path = _normalize_path(route.path)
        if path in IGNORED_PATHS:
            continue
        methods = {m for m in route.methods if m in ALLOWED_METHODS}
        if not methods:
            continue
        routes.setdefault(path, set()).update(methods)
    return routes


def _filter_contract_paths(
    routes: Dict[str, Set[str]], allowed_extensions: Set[str]
) -> Dict[str, Set[str]]:
    contract_routes: Dict[str, Set[str]] = {}
    for path, methods in routes.items():
        if path.startswith("/API/1.1/") or path in allowed_extensions:
            contract_routes[path] = methods
    return contract_routes


def _diff(a: Iterable[str], b: Iterable[str]) -> Set[str]:
    return set(a) - set(b)


def test_local_routes_are_documented_or_allowed():
    swagger_methods = _load_swagger_methods()
    allowed_extensions = _load_allowed_extensions()
    local_routes = _collect_local_routes()
    contract_routes = _filter_contract_paths(local_routes, allowed_extensions)

    unexpected = sorted(
        path
        for path in contract_routes.keys()
        if path not in swagger_methods and path not in allowed_extensions
    )
    assert not unexpected, f"Rutas locales fuera de Swagger sin documentar: {unexpected}"


def test_local_methods_are_subset_of_swagger_for_official_paths():
    swagger_methods = _load_swagger_methods()
    allowed_extensions = _load_allowed_extensions()
    local_routes = _collect_local_routes()
    contract_routes = _filter_contract_paths(local_routes, allowed_extensions)

    mismatches = []
    for path, local_methods in contract_routes.items():
        if path not in swagger_methods:
            continue
        allowed = swagger_methods[path]
        extra = _diff(local_methods, allowed)
        if extra:
            mismatches.append(f"{path}: {sorted(extra)}")

    assert not mismatches, (
        "Metodos locales fuera de Swagger: " + "; ".join(mismatches)
    )
