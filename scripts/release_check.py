#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CheckStep:
    name: str
    command: List[str]


def _python_cmd(*args: str) -> List[str]:
    return [sys.executable, *args]


STEPS = [
    CheckStep(
        name="Contrato Swagger",
        command=_python_cmd("-m", "pytest", "-q", "-m", "contract"),
    ),
    CheckStep(
        name="Cobertura minima por suite",
        command=_python_cmd("scripts/run_coverage_suite.py", "all"),
    ),
    CheckStep(
        name="Politicas de runtime",
        command=_python_cmd(
            "-m",
            "pytest",
            "-q",
            "tests/test_runtime_mode_policy.py",
            "tests/test_runtime_policy_unit.py",
        ),
    ),
    CheckStep(
        name="Smoke HTTP transporte",
        command=_python_cmd("-m", "pytest", "-q", "tests/test_api_http_smoke.py"),
    ),
    CheckStep(
        name="Logs y observabilidad",
        command=_python_cmd(
            "-m",
            "pytest",
            "-q",
            "tests/test_shared_logger.py",
            "tests/test_observability_api.py",
        ),
    ),
]


def main() -> int:
    for step in STEPS:
        print(f"[release-check] {step.name}")
        rc = subprocess.run(step.command).returncode
        if rc != 0:
            print(f"[release-check] FAIL: {step.name}")
            return rc
        print(f"[release-check] OK: {step.name}")
    print("[release-check] OK: todas las validaciones pasaron")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
