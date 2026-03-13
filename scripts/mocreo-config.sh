#!/usr/bin/env bash
# MOCREO one-time credential setup.
# Guides you through platform selection (Sensor System / Smart System)
# and prompts for your account email and password (input is hidden).
# Credentials are stored only in the local .env file.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

# Resolve Python: prefer project venv, then system python3/python
if [ -f "$ROOT_DIR/venv/bin/python" ]; then
    PYTHON="$ROOT_DIR/venv/bin/python"
elif [ -f "$ROOT_DIR/venv/Scripts/python.exe" ]; then
    PYTHON="$ROOT_DIR/venv/Scripts/python.exe"
elif command -v python3 &>/dev/null; then
    PYTHON="python3"
else
    PYTHON="python"
fi

exec "$PYTHON" "$ROOT_DIR/scripts/bootstrap_credentials.py" "$@"
