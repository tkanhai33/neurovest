#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "========================================="
echo "PHASE 1B - PYTHON RUNTIME SETUP"
echo "========================================="
echo

#############################################
# Update Contract
#############################################

mkdir -p "$ROOT/docs/contracts"

cat > "$ROOT/docs/contracts/PHASE_1B_PYTHON_RUNTIME_AMENDMENT.md" <<'EOF'
# Phase 1B Python Runtime Amendment

## Development Runtime

Primary runtime:

Python 3.14

## Fallback Runtime

Python 3.12 may be used later if a required dependency proves incompatible with Python 3.14.

## Reason

The current development machine:

- Ubuntu 26.04
- System Python: 3.14.4

Using the system Python avoids:

- maintaining multiple Python installations
- custom repositories
- unnecessary complexity

## Contract Rule

Development proceeds on Python 3.14 unless package compatibility requires reverting to Python 3.12.
EOF

echo "PASS: Runtime amendment written."
echo

#############################################
# Verify Python
#############################################

if ! command -v python3.14 >/dev/null 2>&1; then
    echo "ERROR: python3.14 not found."
    exit 1
fi

echo "System Python:"
python3.14 --version
echo

#############################################
# Create VENV
#############################################

cd "$BACKEND"

if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3.14 -m venv .venv
else
    echo ".venv already exists."
fi

source .venv/bin/activate

echo
echo "Active Python:"
python --version
echo

#############################################
# Upgrade pip
#############################################

echo "Upgrading pip..."
pip install --upgrade pip

#############################################
# Install dependencies
#############################################

echo
echo "Installing Phase 1 dependencies..."

pip install \
    fastapi \
    "uvicorn[standard]" \
    pydantic \
    pydantic-settings \
    sqlalchemy \
    "psycopg[binary]" \
    alembic \
    pytest

echo
echo "Installed packages:"
pip list
echo

#############################################
# Verify imports
#############################################

echo "Verifying imports..."

python - <<'PY'
import fastapi
import sqlalchemy
import psycopg
import alembic
import pytest

print("PASS: All imports successful.")
PY

echo

#############################################
# Run Tests
#############################################

echo "Running pytest..."
pytest || true

echo
echo "========================================="
echo "PHASE 1B COMPLETE"
echo "========================================="
echo
echo "To activate the environment later:"
echo
echo "cd ~/Neurovest/backend"
echo "source .venv/bin/activate"
echo
echo "To start the API:"
echo
echo "cd ~/Neurovest/backend"
echo "source .venv/bin/activate"
echo "uvicorn app.main:app --reload"
echo
echo "Health endpoint:"
echo "http://127.0.0.1:8000/health"
echo
echo 'Expected response:'
echo '{'
echo '  "status": "ok",'
echo '  "phase": "phase_1_skeleton",'
echo '  "live_trading": "locked",'
echo '  "broker_orders": "locked"'
echo '}'
