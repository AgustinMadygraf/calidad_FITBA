#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class SuiteConfig:
    marker: str
    fail_under: int


SUITES: Dict[str, SuiteConfig] = {
    "unit": SuiteConfig(marker="unit", fail_under=70),
    "integration": SuiteConfig(marker="integration", fail_under=60),
    "api_http": SuiteConfig(marker="api_http", fail_under=65),
    "contract": SuiteConfig(marker="contract", fail_under=45),
}


def _run_suite(name: str, *, cov_target: str) -> int:
    config = SUITES[name]
    env = os.environ.copy()
    env["COVERAGE_FILE"] = f".coverage.{name}"
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "-m",
        config.marker,
        "--cov",
        cov_target,
        "--cov-report",
        "term",
        "--cov-fail-under",
        str(config.fail_under),
    ]
    print(f"[coverage] Running suite '{name}' (min {config.fail_under}%)")
    return subprocess.run(cmd, env=env).returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run pytest coverage thresholds by suite."
    )
    parser.add_argument(
        "suite",
        choices=[*SUITES.keys(), "all"],
        help="Suite to run or 'all' for all suites.",
    )
    parser.add_argument(
        "--cov-target",
        default="src",
        help="Coverage target package/path (default: src).",
    )
    args = parser.parse_args()

    if args.suite == "all":
        exit_code = 0
        for suite_name in SUITES:
            rc = _run_suite(suite_name, cov_target=args.cov_target)
            if rc != 0:
                exit_code = rc
        return exit_code

    return _run_suite(args.suite, cov_target=args.cov_target)


if __name__ == "__main__":
    raise SystemExit(main())
