#!/usr/bin/env bash
set -euo pipefail

echo "Testing talos-configuration..."

if [[ ! -x ".venv/bin/python" ]]; then
  python3 -m venv .venv
fi

PIP_DISABLE_PIP_VERSION_CHECK=1 PIP_NO_CACHE_DIR=1 .venv/bin/python -m pip install -q -r requirements.txt pytest pytest-asyncio httpx -e ../../contracts/python
PYTHONPATH=. .venv/bin/python -m pytest -q

echo "talos-configuration tests passed."
