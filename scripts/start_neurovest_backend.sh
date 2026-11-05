#!/usr/bin/env bash

set +e
set +u
set +H

REPO_ROOT="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.." \
      && pwd
)"

cd "$REPO_ROOT" || {
    echo "BLOCKED: NeuroVest repository could not be opened."
    return 1 2>/dev/null || exit 1
}

VENV_ACTIVATE="$REPO_ROOT/.venv/bin/activate"

if [ ! -f "$VENV_ACTIVATE" ]; then
    echo "BLOCKED: Python virtual environment is missing:"
    echo "  $VENV_ACTIVATE"
    return 1 2>/dev/null || exit 1
fi

source "$VENV_ACTIVATE"

ENV_FILE="$REPO_ROOT/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "BLOCKED: persistent NeuroVest environment file is missing:"
    echo "  $ENV_FILE"
    return 1 2>/dev/null || exit 1
fi

ENV_MODE="$(
    stat -c '%a' "$ENV_FILE" 2>/dev/null
)"

if [ "$ENV_MODE" != "600" ]; then
    echo "BLOCKED: persistent environment file must be mode 0600."
    echo "Actual mode:"
    echo "  ${ENV_MODE:-UNKNOWN}"
    return 1 2>/dev/null || exit 1
fi

set -a

# Persistent deployment environment is intentionally outside Git.
# shellcheck disable=SC1090
source "$ENV_FILE"

set +a

if [ -z "${NEUROVEST_JWT_SECRET-}" ]; then
    echo "BLOCKED: persistent environment did not provide"
    echo "NEUROVEST_JWT_SECRET."
    return 1 2>/dev/null || exit 1
fi

if [ "${#NEUROVEST_JWT_SECRET}" -lt 32 ]; then
    echo "BLOCKED: persistent JWT secret is unexpectedly short."
    return 1 2>/dev/null || exit 1
fi

HOST="${NEUROVEST_BACKEND_HOST:-127.0.0.1}"
PORT="${NEUROVEST_BACKEND_PORT:-8000}"

echo
echo "======================================================================"
echo "NEUROVEST BACKEND"
echo "======================================================================"
echo
echo "Repository:"
echo "  $REPO_ROOT"
echo
echo "JWT environment:"
echo "  $ENV_FILE"
echo
echo "JWT secret:"
echo "  PRESENT — REDACTED"
echo
echo "Listening:"
echo "  http://${HOST}:${PORT}"
echo

exec uvicorn \
  --timeout-graceful-shutdown 25 \
  backend.app.main:app \
  --host "$HOST" \
  --port "$PORT"
