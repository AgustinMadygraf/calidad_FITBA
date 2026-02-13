#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [[ ! -f "venv/bin/activate" ]]; then
  echo '[ERROR] No se encontro "venv/bin/activate".'
  echo 'Crea el entorno virtual con: python3 -m venv venv'
  exit 1
fi

# shellcheck disable=SC1091
source "venv/bin/activate"

if [[ ! -f "run.py" ]]; then
  echo "[ERROR] No se encontro \"run.py\" en \"$PWD\"."
  exit 1
fi

python run.py "$@"
